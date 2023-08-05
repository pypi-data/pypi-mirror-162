"""class for Robot Framework-driven RPA using TOS."""
import sys
from copy import deepcopy

from packaging.version import Version, parse
import robot
from robot.api import logger
from robot.api.deco import keyword
from robot.errors import ExecutionFailed, PassExecution, RobotError

from robot.libraries.BuiltIn import BuiltIn
from robot.running import EXECUTION_CONTEXTS as EC
from robot.running.model import TestCase
from robot.version import VERSION as RF_VERSION

from RPALibrary.helpers import get_stage_from_tags

from tos.statuses import Status
from TOSLibrary import TOSLibrary
from TOSLibrary.dynamic_library import DynamicLibrary

from .exceptions import ExceptionRaisers
from .helpers import get_error_handler_from_tags, stage_is_transactional


def is_rf4():
    return parse(RF_VERSION) >= Version("4")


class RPAListener(DynamicLibrary):  # noqa
    """
    RPAListener class is used for automatic handling of task objects to be worked
    by RPA stage definitions that have been defined in Robot Framework script.
    """

    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(
        self,
        db_server,
        db_name,
        db_user=None,
        db_passw=None,
        db_auth_source=None,
        collection_suffix="",
        separate_payloads=False,
        payloads_ttl=0,
        item_variable_name="ITEM",
        item_identifier_field=None,
        collection_prefix="",
        mongo_client_options=dict(),
    ):
        """
        :param db_server: Mongodb server uri and port, e.g. 'localhost:27017'
        :type db_server: str
        :param db_name: Database name.
        :type db_name: str
        :param db_user: Database username.
        :type db_user: str
        :param db_passw: Database password.
        :type db_passw: str
        :param db_auth_source: Authentication database.
        :type db_auth_source: str
        :param collection_suffix: Suffix for collection. (task_objects.suffix)
        :type collection_suffix: str
        :param separate_payloads: Optionally separate payloads to separate collection
        :type separate_payloads: bool
        :param payloads_ttl: Optional lifetime for separate payloads.
            Either seconds or timestring (for example '30 days' or '1h 10s')
        :type payloads_ttl: Union[int, str]
        :param item_variable_name: The variable name used to refer to task object payload. Defaults to "ITEM".
        :type item_variable_name: str
        :param item_identifier_field: The payload field name used to identify task object in logs. Defaults to "ITEM".
        :type item_identifier_field: str
        :param collection_prefix: Prefix for collection. (prefix.task_objects)
        :type collection_prefix: str
        :param mongo_client_options: Extra options to be passed to mongo client
        :type mongo_client_options: dict
        """

        self._exit_if_not_supported_RF_version()
        super(RPAListener, self).__init__()
        self.ROBOT_LIBRARY_LISTENER = self

        self.item_variable_name = item_variable_name
        self.item_identifier_field = item_identifier_field
        try:
            self.tos = TOSLibrary(
                db_server=db_server,
                db_name=db_name,
                db_user=db_user,
                db_passw=db_passw,
                db_auth_source=db_auth_source,
                collection_suffix=collection_suffix,
                collection_prefix=collection_prefix,
                separate_payloads=separate_payloads,
                payloads_ttl=payloads_ttl,
                mongo_client_options=mongo_client_options,
            )
        except NameError:
            raise
        except Exception as e:
            logger.error(e)
            logger.error("TOS connection failed. Check connection details.")
            sys.exit(-1)

        self.current_item = None
        self.add_component(self)
        self.add_component(self.tos)
        self.add_component(ExceptionRaisers())

        self.current_stage = None
        self.skipped_task_objects = []

    def _exit_if_not_supported_RF_version(self):
        if parse(RF_VERSION) < Version("3.2"):
            logger.error("RPAListener requires Robot Framework version 3.2 or newer")
            sys.exit(-1)

    @property
    def current_item(self):
        return self.__current_item

    @current_item.setter
    def current_item(self, task_object):
        """Sets two variables to robot scope:
            ${ITEM} is a copy of the work item's payload (dictionary),
            ${ITEM_ID} is the item's MongoDB ObjectId

        By default, ${ITEM} is used as the name of the dictionary variable,
        but this can be overriden upon library import with the ``item_identifier_field`` argument.
        """
        self.__current_item = task_object
        if task_object:
            BuiltIn().set_suite_variable(
                f"${self.item_variable_name}", task_object.get("payload")
            )
            BuiltIn().set_suite_variable("$ITEM_ID", str(task_object["_id"]))

    def _start_suite(self, data, result):
        """Initializes the suite (root-level or process stage)

        For transactional stages (`repeat` in test tags), prepares the initial iteration
        by calling ``_prepare_next_task`` and adds setup and teardown keywords for the stage
        if the stage includes them, or if defaults have been set in the robot Settings-table.

        Non-transactional stages are left untouched.
        """

        if data.parent:
            if not data.source == data.parent.source:
                logger.error(
                    "It looks like you are calling robot to run multiple suites. "
                    "This is not supported. Stopping..."
                )
                sys.exit(-1)

        task_template = data.tests[0]
        self.current_stage = get_stage_from_tags(task_template.tags)

        if not data.parent:
            # only run once, for the root suite
            self._prepare_root_suite(data)

        elif stage_is_transactional(task_template):
            # TODO: Remove when dropping support for RF3
            if not is_rf4():
                setup, teardown = (
                    task_template.keywords.setup,
                    task_template.keywords.teardown,
                )
            else:
                setup = task_template.setup
                teardown = task_template.teardown

            if setup:
                try:
                    setup.run(EC.top)
                except RobotError as e:
                    logger.error(f"Stage setup failed.")
                    data.tests = []
                    raise e

            if teardown:
                if is_rf4():
                    data.teardown = teardown
                else:
                    data.keywords.teardown = teardown

            self._prepare_next_task(data.tests.pop(0))

        return

    def _prepare_root_suite(self, root_suite):
        """Prepares the suite definition into a runnable RPA process

        This method does not return anything, instead the root suite is manipulated in place.
        In the resulting suite, each robot task is wrapped into its own child suite.
        The stages are automatically sorted based on their numbering (``stage_n`` tags).

        In order for the listener methods to be called, the listener has to be registered in child suites.
        Currently, this is achieved by taking a deepcopy of the root suite to use as the basis of child suites.
        """

        suite_template = deepcopy(root_suite)
        suite_template.tests = []
        if not is_rf4():
            suite_template.keywords = []
        for test in sorted(
            root_suite.tests, key=lambda test: get_stage_from_tags(test.tags)
        ):
            # TODO: Any other way of extending the listener to the child suites?
            suite_wrapper = deepcopy(suite_template)
            suite_wrapper.name = test.name
            suite_wrapper.tests = [test.deepcopy()]
            root_suite.suites.append(suite_wrapper)

        root_suite.tests.clear()

    def _get_item_id(self, item):
        """Returns the value of the item's identifying field.

        By default, ObjectId is used as the id-field but this can be overriden
        upon library import with the ``item_identifier_field`` argument.
        """

        return item["payload"].get(self.item_identifier_field, None) or str(
            self.current_item["_id"]
        )

    def _prepare_next_task(self, data: TestCase):
        """Prepares the task iteration for execution

        Sets a new work item to the robot scope and appends the suite with a copy of the current
        robot task if another workable item for the current stage was found in the database.

        Returns True if a task iteration was added and False otherwise.
        """
        self.current_item = self._get_one_task_object(self.current_stage)
        if self.current_item:
            self.tos.update_stage_object(self.current_item["_id"], self.current_stage)
            data.parent.tests.append(
                RPATask(name=self._get_item_id(self.current_item), task_template=data)
            )
            return True
        else:
            return None

    def _end_test(self, data, result):

        new_status = None
        if stage_is_transactional(data) and self.current_item:
            new_status = self._update_task_object_stage_and_status(
                self.current_item["_id"], self.current_stage, result
            )

        should_exit_stage = False

        if not result.passed:

            should_exit_stage = True
            # TODO: Will future versions of robotframework allow a better way
            #       for inspecting the exception type?
            explicit_error_handler = get_error_handler_from_tags(data.tags)
            error_handler_status = None

            if explicit_error_handler:
                error_handler_status, msg = BuiltIn().run_keyword_and_ignore_error(
                    explicit_error_handler
                )

            if error_handler_status == "FAIL":
                result.status = "FAIL"
                result.message = f"Error handler failed: {msg}"

            elif "BusinessException" in result.message or new_status == Status.SKIP:
                should_exit_stage = False

        self.current_item = None

        if not should_exit_stage:
            self._prepare_next_task(data)

    def _update_task_object_stage_and_status(self, to_id, current_stage, result):
        if getattr(result, "skipped", None) or to_id in self.skipped_task_objects:
            new_status = Status.SKIP
            self.tos.update_exceptions(to_id, current_stage, result.message)
        elif result.passed:
            new_status = Status.PASS
        else:
            new_status = Status.FAIL
            self.tos.update_exceptions(to_id, current_stage, result.message)

        self.tos.set_stage_end_time(to_id, current_stage)
        self.tos.update_status(to_id, self.current_stage, new_status)

        return new_status

    def _get_one_task_object(self, stage=None):
        """
        Gets one work item to be processed by stage with index ``stage``
        """
        if not stage:
            stage = self.current_stage

        getter_args = {
            "statuses": ["pass", "new"],
            "stages": stage - 1,
        }

        return self.tos.find_one_task_object_by_status_and_stage(**getter_args)

    @keyword
    def update_current_item(self, *key_value_pairs, **items):
        """Update the contents of the currently worked item's payload in the database.

        The database document will be upserted with values from the item's payload dictionary at the time of calling.
        Additional variables can be added with the given ``key_value_pairs`` and ``items``.

        Giving items as ``key_value_pairs`` means giving keys and values
        as separate arguments:

        | Set To Dictionary | ${D1} | key | value | second | ${2} |
        =>
        | ${D1} = {'a': 1, 'key': 'value', 'second': 2}

        | Set To Dictionary | ${D1} | key=value | second=${2} |

        The latter syntax is typically more convenient to use, but it has
        a limitation that keys must be strings.

        If given keys already exist in the dictionary, their values are updated.
        """
        dictionary = self.current_item["payload"]

        def set_to_dict():
            if len(key_value_pairs) % 2 != 0:
                raise ValueError(
                    "Adding data to a dictionary failed. There "
                    "should be even number of key-value-pairs."
                )
            for i in range(0, len(key_value_pairs), 2):
                dictionary[key_value_pairs[i]] = key_value_pairs[i + 1]
            dictionary.update(items)
            return dictionary

        self.update_payload(self.current_item["_id"], set_to_dict())
        logger.info(f"'{self.current_item['_id']}' was updated.")
        logger.debug(
            f"'{self.current_item['_id']}'payload contents after update: {self.current_item['payload']}"
        )

    @keyword
    def run_keyword_and_skip_on_failure(self, name, *args):
        """Runs the keyword and sets task object status to `skip` if failure occurs.

        The keyword to execute and its arguments are specified using `name` and `*args` exactly like with Run Keyword.

        `Skip Task Object` is called conditionally based on the execution result,
        causing rest of the current keyword and task to be skipped in case of failure.

        The error message from the executed keyword is printed to the console andset to the task object's
        exception field.

        Process execution proceeds with the next task object.

        Example:
        | Run Keyword And Skip On Failure | Should Be True | ${invoice_amount} > 0 |
        ...    msg=Invoice is for a zero amount, no action required
        """
        try:
            return BuiltIn().run_keyword(name, *args)
        except ExecutionFailed as err:
            if err.syntax:
                # Keyword was called with wrong number of arguments etc.
                raise err
            self.skip_task_object(reason=err.message)

    @keyword
    def skip_task_object(self, reason, to_id=None):
        """Sets the task object status to `skip` and skips rest of the current task.

        By default, targets the current task object.
        Object id is persisted in class attribute `skipped_task_objects`.
        """
        if not to_id:
            to_id = self.current_item["_id"]

        # TODO: Make this the default when dropping support for RF 3
        if is_rf4():
            raise robot.api.exceptions.SkipExecution(reason)

        else:
            self.skipped_task_objects.append(to_id)
            logger.warn(f"Skipping {to_id}: {reason}")
            raise PassExecution(reason)


class RPATask(TestCase):
    """RPATask object is created for each task iteration in a transactional RPA process stage"""

    def __init__(self, name, task_template):
        super().__init__(
            name=str(name),
            doc=task_template.doc,
            tags=task_template.tags,
            timeout=task_template.timeout,
            lineno=task_template.lineno,
        )
        if is_rf4():
            self.body = task_template.body
        else:
            self.keywords = task_template.keywords.normal
        self.tags = task_template.tags
