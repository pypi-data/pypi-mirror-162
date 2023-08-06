"""Client for Kameleoon"""
import json
import threading
import time
from json import JSONDecodeError
from typing import Optional, Union, Any, Type, List, Dict, Literal
from urllib.parse import urlencode
import warnings
from dateutil import parser

import requests
from requests import Response
from kameleoon.client_configuration import KameleoonClientConfiguration

from kameleoon.data import Conversion, get_nonce, Data
from kameleoon.defaults import DEFAULT_BLOCKING, DEFAULT_CONFIGURATION_PATH, DEFAULT_TIMEOUT_MILLISECONDS, \
    DEFAULT_VISITOR_DATA_MAXIMUM_SIZE, DEFAULT_CONFIGURATION_UPDATE_INTERVAL
from kameleoon.version import __version__ as kameleoon_python_version

from kameleoon.exceptions import ConfigurationNotFoundException, CredentialsNotFoundException, \
    ExperimentConfigurationNotFound, NotTargeted, NotActivated, SiteCodeDisabled, VariationConfigurationNotFound,\
    FeatureConfigurationNotFound, FeatureVariableNotFound
from kameleoon.helpers.functions import check_visitor_code, obtain_hash_double, get_size, read_kameleoon_cookie_value
from kameleoon.helpers.logger import get_logger
from kameleoon.helpers.config import config
from kameleoon.targeting.models import Segment
from kameleoon.query_graphql import query_ql_experiments, query_ql_feature_flags

__all__ = ["KameleoonClient", ]

REFERENCE = 0
X_PAGINATION_PAGE_COUNT = "X-Pagination-Page-Count"
SEGMENT = "targetingSegment"
KAMELEOON_TRACK_EXPERIMENT_THREAD = "KameleoonTrackExperimentThread"
KAMELEOON_TRACK_DATA_THREAD = "KameleoonTrackDataThread"
KAMELEOON_ACTIVATE_FEATURE_THREAD = "KameleoonActivateFeatureThread"
STATUS_ACTIVE = "ACTIVE"
FEATURE_STATUS_DEACTIVATED = "DEACTIVATED"


class KameleoonClient:
    """
    KameleoonClient

    Example:

    .. code-block:: python3

        from kameleoon import KameleoonClient

        SITE_CODE = 'a8st4f59bj'

        kameleoon_client = KameleoonClient(SITE_CODE)

        kameleoon_client = KameleoonClient(SITE_CODE, blocking=False,
                           configuration_path='/etc/kameleoon/client-python.yaml')

        kameleoon_client = KameleoonClient(SITE_CODE, blocking=True)

        kameleoon_client = KameleoonClient(SITE_CODE, blocking=True, logger=MyLogger)
    """
    initialize = False
    timer: Optional[threading.Timer] = None

    # pylint: disable=R0913
    def __init__(
            self, site_code: str,
            blocking: bool = DEFAULT_BLOCKING,
            configuration_path: str = DEFAULT_CONFIGURATION_PATH,
            configuration_object: Optional[KameleoonClientConfiguration] = None,
            logger=None
    ):
        """
        :param site_code: Code of the website you want to run experiments on. This unique code id can
                              be found in our platform's back-office. This field is mandatory.
        :type site_code: str

        :param blocking: This parameter defines if the trigger_experiment() method has a non-blocking or
                               blocking behavior. Value true will set it to be blocking.
                               This field is optional and set to False by default.
        :type blocking: bool
        :param configuration_path: Path to the SDK configuration file.
                                   This field is optional and set to /etc/kameleoon/client-python.yaml by default.
        :type configuration_path: str
        :param configuration:   Configuration object which can be used instead of external file at configuration_path.
                                This field is optional set to None by default.
        :type configuration: KameleoonClientConfiguration
        :param logger: Optional component which provides a log method to log messages. By default see method get_logger.
        """
        # pylint: disable=too-many-instance-attributes
        # Eight is reasonable in this case.
        self.site_code = site_code
        self.blocking = blocking
        self.experiments: List[Dict[str, Any]] = []
        self.feature_flags: List[Dict[str, str]] = []
        self.logger = logger or get_logger()
        self.automation_base_url = "https://api.kameleoon.com/"
        self.api_data_url = "https://api-data.kameleoon.com/"
        self._setup_client_configuration(configuration_path, configuration_object)
        auth_resp = self._obtain_access_token()
        if auth_resp:
            self.access_token = auth_resp['access_token']

        self.data: Dict[str, List[Type[Data]]] = {}

        self._init_fetch_configuration()

    def __del__(self):
        if self.timer is not None:
            self.timer.cancel()

    def make_sync_request(self, url: str, headers: Dict[str, str],
                          filters: Optional[List[Dict[str, Union[str, List[Union[str, int]]]]]] = None,
                          payload=None,
                          method: Literal['post', 'get'] = 'post',
                          timeout: Optional[int] = None) -> Optional[Any]:
        """
        :param url: API URL
        :type url: str
        :param headers: request headers
        :type headers: dict
        :param filters: filters
        :type filters: dict
        :param payload: post data or get params dict
        :type payload: any
        :param method: post or get, defaults to post
        :type method: Literal['post', 'get']
        :param timeout: requests timeout
        :type timeout: int
        :return:
        """

        # pylint: disable=too-many-arguments
        if payload is None:
            payload = {}
        if filters:
            payload['filter'] = json.dumps(filters)
        resp_dict: Any = {}
        if method == 'post':
            try:
                resp_dict = requests.post(url, data=payload, headers=headers, timeout=timeout)
            except requests.exceptions.RequestException as ex:
                self.logger.error(ex)
        else:
            try:
                resp_dict = requests.get(url, params=payload, headers=headers, timeout=timeout)
            except requests.exceptions.RequestException as ex:
                self.logger.error(ex)
        if not resp_dict or resp_dict.ok is not True:
            self.logger.error("Failed to fetch %s", resp_dict)
            return None
        try:
            resp = resp_dict.json()
        except JSONDecodeError:
            resp = None
            if isinstance(resp_dict, (Dict, str, Response)):
                resp = resp_dict
        return resp

    def _fetch_all(self,
                   url: str, headers: Dict[str, str],
                   filters=None, payload=None,
                   timeout=None):
        """
        Getting data from multiple data pages
        :param url: API URL
        :param headers: request headers
        :param filters:
        :param payload: post data or get params dict
        :param timeout: requests timeout
        :return:
        """
        # pylint: disable=too-many-arguments,no-self-use
        if payload is None:
            payload = {}
        if filters:
            payload['filter'] = json.dumps(filters)
        results = []
        current_page = 1
        while True:
            payload['page'] = current_page
            http = None
            try:
                http = requests.get(url, params=payload, headers=headers, timeout=timeout)
            except requests.ConnectionError as ex:
                self.logger.error(ex)
            if not http:
                break
            results += http.json()
            if X_PAGINATION_PAGE_COUNT in http.headers and int(
                    http.headers[X_PAGINATION_PAGE_COUNT]) <= current_page:
                break
            current_page += 1
        return results

    def _fetch_all_graphql(self,
                           url: str, data: str, headers: Dict[str, str],
                           timeout=None):
        """
        Getting data from multiple data pages
        :param url: API URL
        :param headers: request headers
        :param filters:
        :param payload: post data or get params dict
        :param timeout: requests timeout
        :return:
        """
        # pylint: disable=too-many-arguments,no-self-use
        results = []
        current_page = 1
        while True:
            http = None
            try:
                http = requests.post(url, data=data, headers=headers, timeout=timeout)
            except requests.ConnectionError as ex:
                self.logger.error(ex)
            if not http:
                break
            results.append(http.json())
            if X_PAGINATION_PAGE_COUNT not in http.headers or (X_PAGINATION_PAGE_COUNT in http.headers and int(
                    http.headers[X_PAGINATION_PAGE_COUNT])) <= current_page:
                break
            current_page += 1
        return results

    def _obtain_access_token(self) -> Optional[Dict[str, str]]:
        """
        :return: Dict
        """
        url = f"{self.automation_base_url}oauth/token"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }
        try:
            client_id = self.config['client_id']
            client_secret = self.config['client_secret']
        except KeyError as ex:
            raise ConfigurationNotFoundException from ex
        body = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        resp = self.make_sync_request(url, headers, method="post", payload=body)
        if resp:
            self.logger.debug("Bearer Token is fetched: %s", resp['access_token'])
            return resp
        self.logger.error("Failed to fetch bearer token")
        return resp

    def obtain_visitor_code(self, cookies: Union[str, Dict[str, str]],
                            default_visitor_code: Optional[str] = None) -> str:
        """
        Load cookies from a string (presumably HTTP_COOKIE) or
        from a dictionary.
        See SimpleCookie() https://docs.python.org/3/library/http.cookies.html

        :param cookies: str ot dict
        :param default_visitor_code: Optional str
        :return: kameleoon_cookie_value
        :rtype: str

        Examples:

        .. code-block:: python3

            kameleoon_client = KameleoonClient(SITE_CODE)

            kameleoon_client.obtain_visitor_code(cookies)

            kameleoon_client.obtain_visitor_code(cookies, default_visitor_code)

        """
        # pylint: disable=no-self-use
        return read_kameleoon_cookie_value(cookies, default_visitor_code)

    def trigger_experiment(self, visitor_code: str, experiment_id: int,  # noqa: C901
                           timeout=DEFAULT_TIMEOUT_MILLISECONDS) -> Optional[int]:
        """  Trigger an experiment.

        If such a visitor_code has never been associated with any variation,
        the SDK returns a randomly selected variation.
        If a user with a given visitor_code is already registered with a variation, it will detect the previously
        registered variation and return the variation_id.
        You have to make sure that proper error handling is set up in your code as shown in the example to the right to
        catch potential exceptions.

        :param visitor_code: Visitor code
        :param experiment_id: Id of the experiment you want to trigger.
        :param timeout:
        :return: variation_id:  Id of the variation

        :raises:

            ExperimentConfigurationNotFound: Raise when experiment configuration is not found
            NotActivated: The visitor triggered the experiment, but did not activate it. Usually, this happens because
                          the user has been associated with excluded traffic
            NotTargeted: The visitor is not targeted by the experiment, as the associated targeting segment conditions
                         were not fulfilled. He should see the reference variation
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                        (empty, or longer than 255 characters)
            SiteCodeDisabled: Raise when the siteCode is not disabled, SDK doesn't work with disabled siteCodes.
                        To make SDK working please enable Site in your account.


        Examples:

        .. code-block:: python

                visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)
                variation_id = 0
                try:
                    variation_id = kameleoon_client.trigger_experiment(visitor_code, 135471)
                except NotActivated as ex:
                    variation_id = 0
                    client.logger.error(ex)
                except NotTargeted as ex:
                    variation_id = 0
                    client.logger.error(ex)
                except ExperimentConfigurationNotFound as ex:
                    variation_id = 0
                    client.logger.error(ex)

                recommended_products_number = 5

                if variation_id == 148382:
                    recommended_products_number = 10
                elif variation_id == 187791:
                    recommended_products_number = 8

                response = JsonResponse({...})
                # set a cookie
                response.set_cookie(**kameleoon_cookie)
        """
        # pylint: disable=too-many-locals,no-else-return,no-else-raise
        check_visitor_code(visitor_code)
        try:
            experiment = [
                experiment for experiment in self.experiments if int(experiment['id']) == int(experiment_id)
            ][0]
        except IndexError as ex:
            raise ExperimentConfigurationNotFound from ex
        if self.blocking:
            timeout = timeout / 1000
            data_not_sent = self._data_not_sent(visitor_code)
            try:
                body: Union[List[str], str] = list(
                    data_instance.obtain_full_post_text_line() for data_instance in  # type: ignore
                    data_not_sent[visitor_code])
            except KeyError:
                body = ''
            path = self._get_experiment_register_url(visitor_code, experiment_id)
            request_options = {"path": path, "body": body}
            self.logger.debug("Trigger experiment request: %s  timeout: %s", request_options, timeout)
            variation_id = self.make_sync_request(f"{self.tracking_base_url}{path}",
                                                  method='post',
                                                  payload=("\n".join(body or '').encode("UTF-8")),
                                                  headers=self._get_headers())
            if not variation_id or isinstance(variation_id, Response):
                self.logger.error("Failed to trigger experiment: %s variation_id %s", experiment_id, variation_id)
                raise ExperimentConfigurationNotFound(message=str(experiment_id))
            elif variation_id in ["null", ""]:
                raise NotTargeted(message=visitor_code)
            elif variation_id == REFERENCE:
                raise NotActivated(message=visitor_code)
            try:
                variation = int(variation_id)
            except (ValueError, TypeError):
                variation = variation_id
            return variation
        else:
            self._check_site_code_enable(experiment)
            visitor_data = self.data[visitor_code] if visitor_code in self.data else []
            if SEGMENT not in experiment or experiment[
                    SEGMENT] is None or experiment[SEGMENT].check_tree(visitor_data):
                threshold = obtain_hash_double(visitor_code, experiment['respoolTime'], experiment['id'])

                for k, value in experiment['deviations'].items():
                    threshold -= value
                    if threshold < 0:
                        self._run_in_threads_if_needed(multi_threading=self.multi_threading,
                                                       func=self.track_experiment,
                                                       args=[visitor_code, experiment_id, k],
                                                       thread_name=KAMELEOON_TRACK_EXPERIMENT_THREAD)
                        try:
                            variation = int(k)
                        except ValueError:
                            variation = 0
                        return variation
                self._run_in_threads_if_needed(multi_threading=self.multi_threading,
                                               func=self.track_experiment,
                                               args=[visitor_code, experiment_id, REFERENCE, True],
                                               thread_name=KAMELEOON_TRACK_EXPERIMENT_THREAD)
                raise NotActivated(message=visitor_code)
            raise NotTargeted(message=visitor_code)

    def _check_data_size(self, visitor_data_maximum_size: int) -> None:
        """
        Checks the memory for exceeding the maximum size
        :param visitor_data_maximum_size: int
        :return: None
        """
        while get_size(self.data) > (visitor_data_maximum_size * (2 ** 20)):
            keys = self.data.keys()
            if len(list(keys)) > 0:
                del self.data[list(keys)[-1]]
            new_data = self.data.copy()
            del self.data
            self.data = new_data
            del new_data
            if get_size({}) >= get_size(self.data):
                break

    def add_data(self, visitor_code: str, *args) -> None:
        """
        To associate various data with the current user, we can use the add_data() method.
        This method requires the visitor_code as a first parameter, and then accepts several additional parameters.
        These additional parameters represent the various Data Types allowed in Kameleoon.

        Note that the add_data() method doesn't return any value and doesn't interact with the Kameleoon back-end
        servers by itself. Instead, all declared data is saved for further sending via the flush() method described
        in the next paragraph. This reduces the number of server calls made, as data is usually grouped
        into a single server call triggered by the execution of flush()

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param args:
        :return: None

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
                kameleoon_client.add_data(visitor_code, Interest(1))
        """
        check_visitor_code(visitor_code)
        try:
            visitor_data_maximum_size = int(self.config['visitor_data_maximum_size'])
        except KeyError:
            visitor_data_maximum_size = DEFAULT_VISITOR_DATA_MAXIMUM_SIZE
        self._check_data_size(visitor_data_maximum_size)
        if args:
            if visitor_code in self.data:
                if not self.data[visitor_code]:
                    self.data[visitor_code] = []
                self.data[visitor_code] += list(args)
            else:
                self.data[visitor_code] = [*args]
        self.logger.debug("Activate feature request")

    def track_conversion(self, visitor_code: str, goal_id: int, revenue: float = 0.0) -> None:
        """
        To track conversion, use the track_conversion() method. This method requires visitor_code and goal_id to track
        conversion on this particular goal. In addition, this method also accepts revenue as a third optional argument
        to track revenue. The visitor_code is usually identical to the one that was used when triggering the experiment.
        The track_conversion() method doesn't return any value. This method is non-blocking as the server
        call is made asynchronously.

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param goal_id: ID of the goal. This field is mandatory.
        :type goal_id: int
        :param revenue: Revenue of the conversion. This field is optional.
        :type revenue: float
        :return: None
        """
        check_visitor_code(visitor_code)
        self.add_data(visitor_code, Conversion(goal_id, revenue))
        self.flush(visitor_code)

    def flush(self, visitor_code: Optional[str] = None):
        """
        Data associated with the current user via add_data() method is not immediately sent to the server.
        It is stored and accumulated until it is sent automatically by the trigger_experiment()
        or track_conversion() methods, or manually by the flush() method.
        This allows the developer to control exactly when the data is flushed to our servers. For instance,
        if you call the add_data() method a dozen times, it would be a waste of ressources to send data to the
        server after each add_data() invocation. Just call flush() once at the end.
        The flush() method doesn't return any value. This method is non-blocking as the server call
        is made asynchronously.


        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: Optional[str]

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
                kameleoon_client.add_data(visitor_code, Interest(1))

                kameleoon_client.flush()

        """
        if visitor_code is not None:
            check_visitor_code(visitor_code)
        self._run_in_threads_if_needed(multi_threading=self.multi_threading,
                                       func=self.track_data,
                                       args=[visitor_code, ],
                                       thread_name=KAMELEOON_TRACK_DATA_THREAD)

    def obtain_variation_associated_data(self, variation_id: int) -> Dict[str, str]:
        """ Obtain variation associated data.

        To retrieve JSON data associated with a variation, call the obtain_variation_associated_data method of our SDK.
        The JSON data usually represents some metadata of the variation, and can be configured on our web application
        interface or via our Automation API.

        This method takes the variationID as a parameter and will return the data as a json string.
        It will throw an exception () if the variation ID is wrong or corresponds to an experiment
        that is not yet online.

        :param variation_id: int  ID of the variation you want to obtain associated data for. This field is mandatory.
        :return: Dict  Data associated with this variationID.

        :raises: VariationNotFound

        Example:

        .. code-block:: python3

                visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)

                experiment_id = 75253

                try:
                    variation_id = kameleoon_client.trigger_experiment(visitor_code, experiment_id)
                    dict_object = kameleoon_client.obtain_variation_associated_data(variation_id)
                    first_name = dict_object["firstName"]
                except VariationNotFound:
                    # The variation is not yet activated on Kameleoon's side,
                    ie the associated experiment is not online
                    pass
        """
        variations = list(filter(lambda variation: variation['id'] == variation_id,
                                 [variation
                                 for variations in [experiment['variations'] for experiment in self.experiments]
                                 for variation in variations]))
        if not variations:
            raise VariationConfigurationNotFound(variation_id)
        variation = variations[0]
        return json.loads(variation['customJson'])

    def activate_feature(self, visitor_code: str,
                         feature_key: Union[int, str],
                         timeout=DEFAULT_TIMEOUT_MILLISECONDS) -> bool:
        """
        To activate a feature toggle, call the activate_feature() method of our SDK. This method takes a visitor_code
        and feature_key (or feature_id) as mandatory arguments to check if the specified feature will be active
        for a given user. If such a user has never been associated with this feature flag, the SDK returns a boolean
        value randomly (true if the user should have this feature or false if not). If a user with a given visitor_code
        is already registered with this feature flag, it will detect the previous featureFlag value.
        You have to make sure that proper error handling is set up in your code as shown in the example to the right
        to catch potential exceptions.


        :param visitor_code: str Unique identifier of the user. This field is mandatory.
        :param feature_key: int or str ID of the experiment you want to expose to a user. This field is mandatory.
        :param timeout: int Timeout (in milliseconds). This parameter is only used in the blocking version of
                            this method, and specifies the maximum amount of time the method can block to wait for a
                            result. This field is optional. If not provided,
                            it will use the default value of 2000 milliseconds.
        :return: bool Value of the feature that is registered for a given visitor_code.


        :raises:

            FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            NotTargeted: Exception indicating that the current visitor / user did not trigger
                         the required targeting conditions for this feature. The targeting conditions are defined
                         via Kameleoon's segment builder.
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                        (empty, or longer than 255 characters)
            SiteCodeDisabled: Raise when the siteCode is not disabled, SDK doesn't work with disabled siteCodes.
                        To make SDK working please enable Site in your account.

        Examples:

        .. code-block:: python3

                visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)
                feature_key = "new_checkout"
                has_new_checkout = False

                try:
                    has_new_checkout = kameleoon_client.activate_feature(visitor_code, feature_key)
                except NotTargeted:
                    # The user did not trigger the feature, as the associated targeting segment conditions were not
                    # fulfilled. The feature should be considered inactive
                    logger.debug(...)
                except FeatureConfigurationNotFound:
                    # The user will not be counted into the experiment, but should see the reference variation
                    logger.debug(...)

                if has_new_checkout:
                    # Implement new checkout code here
        """
        # pylint: disable=no-else-return
        check_visitor_code(visitor_code)
        self._check_feature_key(feature_key)
        feature_flag = self.get_feature_flag(feature_key)
        data_not_sent = self._data_not_sent(visitor_code)
        if self.blocking:
            connexion_options = {"connect_timeout": int(timeout / 1000.0)}
            try:
                body: Union[List[str], str] = [
                    data_instance.obtain_full_post_text_line() for data_instance in  # type: ignore
                    data_not_sent[visitor_code]]
            except KeyError:
                body = ''
            request_options = {
                "path": self._get_experiment_register_url(visitor_code, feature_flag['id']),
                "body": ("\n".join(body).encode("UTF-8")),
                "headers": {"Content-Type": "text/plain"}
            }
            self.logger.debug("Activate feature request: %s", connexion_options)
            self.logger.debug("Activate feature request: %s", request_options)
            resp = self.make_sync_request(f"{self.tracking_base_url}{request_options['path']}",
                                          headers=self._get_headers(),
                                          payload=request_options['body'],
                                          timeout=connexion_options["connect_timeout"])
            if not resp:
                self.logger.error("Failed to get activation: %s", resp)
                raise FeatureConfigurationNotFound(feature_flag['id'])
            return resp != "null"
        else:
            try:
                visitor_data = self.data[visitor_code]
            except KeyError:
                visitor_data = []
            self._check_site_code_enable(feature_flag)
            if SEGMENT not in feature_flag or feature_flag[SEGMENT] is None or feature_flag[
                    SEGMENT].check_tree(visitor_data):
                if self._feature_flag_scheduled(feature_flag, time.time()):
                    threshold = obtain_hash_double(visitor_code, {}, feature_flag['id'])
                    track_info = []
                    if threshold >= 1 - feature_flag['expositionRate']:
                        variations_id = None
                        if feature_flag["variations"]:
                            variations_id = feature_flag["variations"][0]
                        track_info = [visitor_code, feature_flag['id'], variations_id]
                        activate = True
                    else:
                        track_info = [visitor_code, feature_flag['id'], REFERENCE, True]
                        activate = False
                    self._run_in_threads_if_needed(multi_threading=self.multi_threading,
                                                   func=self.track_experiment,
                                                   args=track_info,
                                                   thread_name=KAMELEOON_ACTIVATE_FEATURE_THREAD)
                    return activate
                else:
                    return False
            else:
                raise NotTargeted(visitor_code)

    # pylint: disable=no-self-use
    def _feature_flag_scheduled(self, feature_flag: Dict[str, Any], date: float) -> bool:
        """
        Checking that feature flag is scheduled then determine its status in current time
        :param feature_flag: Dict[str, Any]
        :return: bool
        """
        current_status = feature_flag['status'] == STATUS_ACTIVE
        if feature_flag['featureStatus'] == FEATURE_STATUS_DEACTIVATED or len(feature_flag['schedules']) == 0:
            return current_status
        for schedule in feature_flag['schedules']:
            if ((schedule.get('dateStart') is None or parser.parse(schedule['dateStart']).timestamp() < date) and
                    (schedule.get('dateEnd') is None or parser.parse(schedule['dateEnd']).timestamp() > date)):
                return True
        return False

    def obtain_feature_variable(self, feature_key: Union[str, int],
                                variable_key: str) -> Union[bool, str, float, Dict[str, Any]]:
        """
        Retrieve a feature variable.
        A feature variable can be changed easily via our web application.

        :param feature_key: Union[str, int] ID or Key of the feature you want to obtain to a user.
                            This field is mandatory.
        :param variable_key: str  Key of the variable. This field is mandatory.
        :return: bool or str or float or dict

        :raises: FeatureVariableNotFound: Exception indicating that the requested variable has not been found.
                                         Check that the variable's ID (or key) matches the one in your code.
                 FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found
                                               in the internal configuration of the SDK. This is usually normal and
                                               means that the feature flag has not yet been activated on
                                               Kameleoon's side.

        Example:

        .. code-block:: python3

                feature_key = "myFeature"
                variable_key = "myVariable"
                try:
                    data = kameleoon_client.obtain_feature_variable(feature_key, variable_key)
                except FeatureConfigurationNotFound:
                    # The feature is not yet activated on Kameleoon's side
                    pass
                except FeatureVariableNotFound:
                    # Request variable not defined on Kameleoon's side
                    pass
        """

        # pylint: disable=no-else-raise
        self._check_feature_key(feature_key)
        feature_flag = self.get_feature_flag(feature_key)
        custom_json = None
        try:
            custom_json = json.loads(feature_flag["variations"][0]['customJson'])[variable_key]
        except (IndexError, KeyError) as ex:
            self.logger.error(ex)
            raise FeatureVariableNotFound(variable_key) from ex
        if not custom_json:
            raise FeatureVariableNotFound(variable_key)
        elif custom_json['type'] == 'Boolean':
            return custom_json['value'] == 'True'
        elif custom_json['type'] == 'String':
            return str(custom_json['value'])
        elif custom_json['type'] == 'Number':
            return float(custom_json['value'])
        elif custom_json['type'] == 'JSON':
            return json.loads(custom_json['value'])
        else:
            raise TypeError("Unknown type for feature variable")

    def retrieve_data_from_remote_source(self,
                                         key: str,
                                         timeout: Optional[int] = DEFAULT_TIMEOUT_MILLISECONDS) -> Optional[Any]:
        """
        The retrieved_data_from_remote_source method allows you to retrieve data (according to a key passed as
        argument)stored on a remote Kameleoon server. Usually data will be stored on our remote servers
        via the use of our Data API. This method, along with the availability of our highly scalable servers
        for this purpose, provides a convenient way to quickly store massive amounts of data that
        can be later retrieved for each of your visitors / users.

        :param key: key you want to retrieve data. This field is mandatory.
        :type key: str
        :param timeout: requests timeout (default value is 2000 milliseconds)
        :type timeout: int

        :return: data assosiated with this key, decoded into json
        :rtype: Optional[Any]

        :raises:

            RequestException: All new network exceptions (timeout / connection refused and etc)
            JSONDecodeError: Exceptions happen during JSON decoding
        """
        return self.make_sync_request(
            url=self._get_api_data_request_url(key),
            method='get',
            headers=self._get_header_client(),
            timeout=timeout)

    def _init_fetch_configuration(self) -> None:
        """
        :return:
        """
        self._fetch_graphql()

    def _fetch(self) -> None:
        """
        fetch_configuration_job task
        :return:  None
        """
        auth_resp = self._obtain_access_token()
        if auth_resp:
            self.access_token = auth_resp['access_token']
        self.logger.debug('Scheduled job to fetch configuration is starting.')
        site = self.obtain_site()
        if site:
            site_id = site[0]['id']
            self.obtain_tests(site_id)
            self.obtain_feature_flags(site_id)
        else:
            self.experiments = self.experiments or []
            self.feature_flags = self.feature_flags or []

    def _fetch_graphql(self) -> None:
        """
        fetch_configuration_job task
        :return:  None
        """
        auth_resp = self._obtain_access_token()
        if auth_resp:
            self.access_token = auth_resp['access_token']
        self.logger.debug('Scheduled job to fetch configuration graphQL is starting.')
        self.obtain_experiments_graphql(self.site_code)
        self.obtain_feature_flags_graphql(self.site_code, self.environment)
        if self.timer is not None:
            self.timer.cancel()

        self._add_fetch_configuration_after_delay()

    def _add_fetch_configuration_after_delay(self) -> None:
        """
        :return: None
        """
        self.timer = threading.Timer(self.actions_configuration_refresh_interval, self._fetch_graphql)
        self.timer.setDaemon(True)
        self.timer.start()

    def _get_header_client(self) -> Dict[str, str]:
        return {
            'Kameleoon-Client': f'sdk/python/{kameleoon_python_version}'
        }

    def _get_headers(self) -> Dict[str, str]:
        """
        :return: request headers with Authorization Bearer token
        """
        if not self.access_token:
            raise CredentialsNotFoundException
        return {**{
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }, **self._get_header_client()}

    def _get_filter(self, field: str,
                    operator: str,
                    parameters: List[Union[str, int]]
                    ) -> Dict[str, Union[str, List[Union[str, int]]]]:
        """
        Filters for request
        :param field:
        :param operator:
        :param parameters:
        :return:
        """
        # pylint: disable=no-self-use
        return {'field': field, 'operator': operator, 'parameters': parameters}

    def obtain_site(self) -> List[Dict[str, Any]]:
        """
        :return: List
        """
        self.logger.debug("Fetching site")
        query_params = {'perPage': 1}
        url = f"{self.automation_base_url}sites"
        headers = self._get_headers()
        filters = [self._get_filter('code', 'EQUAL', [self.site_code])]
        sites = self.make_sync_request(url, headers=headers, payload=query_params, method='get', filters=filters)
        return sites  # type: ignore

    def obtain_variation(self, variation_id: int):
        """

        :param variation_id:
        :return:
        """
        return self.make_sync_request(f"{self.automation_base_url}variations/{variation_id}",
                                      method='get',
                                      headers=self._get_headers())

    def obtain_segment(self, segment_id: int):
        """

        :param segment_id:
        :return:
        """
        return self.make_sync_request(f"{self.automation_base_url}segments/{segment_id}",
                                      method='get',
                                      headers=self._get_headers())

    # fetching segment for both types: experiments and feature_flags (campaigns)
    # pylint: disable=no-self-use
    def _complete_campaign_graphql(self, campaign) -> Dict[str, Any]:
        """
        :param campaign (experiment or feature_flag):
        :type: dict
        :return: campaign (experiment or feature_flag)
        :rtype: dict
        """
        campaign['id'] = int(campaign['id'])
        campaign['status'] = campaign['status']
        if 'respoolTime' in campaign and campaign['respoolTime'] is not None:
            campaign['respoolTime'] = {
                ('origin' if respoolTime['variationId'] == "0" else respoolTime['variationId']):
                respoolTime['value'] for respoolTime in campaign['respoolTime']}
        if 'variations' in campaign and campaign['variations'] is not None:
            campaign['variations'] = [{'id': int(variation['id']), 'customJson': variation['customJson']}
                                      for variation in campaign['variations']]
        if 'segment' in campaign and campaign['segment'] is not None:
            campaign['targetingSegment'] = Segment(campaign['segment'])
        return campaign

    def _complete_experiment_graphql(self, experiment) -> Dict[str, Any]:
        """
        :param experiment:
        :type: dict
        :return:  experiment
        :rtype: dict
        """
        if 'deviations' in experiment and experiment['deviations'] is not None:
            experiment['deviations'] = {
                ('origin' if deviation['variationId'] == "0" else deviation['variationId']):
                deviation['value'] for deviation in experiment['deviations']}
        return self._complete_campaign_graphql(experiment)

    def _complete_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """
        :param experiment:
        :type: dict
        :return:  experiment
        :rtype: dict
        """
        variations = []
        if 'variations' in experiment:
            for variation_id in experiment['variations']:
                variation = self.obtain_variation(variation_id)
                variations.append(variation)
            experiment['variations'] = variations
        if 'targetingSegmentId' in experiment:
            experiment['targetingSegment'] = Segment(self.obtain_segment(experiment['targetingSegmentId']))
        return experiment

    def obtain_experiments_graphql(self, site_code: str, per_page=-1) -> List[Dict[str, Any]]:
        """
        Obtain experiments with GraphQL
        :param site_id:
        :param per_page:
        :return: None
        """
        self.logger.debug("Fetching experiments")
        experiments = self._fetch_all_graphql(f"{self.automation_base_url}v1/graphql?perPage={per_page}",
                                              data=query_ql_experiments(site_code),
                                              headers=self._get_headers())
        experiments = [experiment['node'] for experimentQL in experiments
                       for experiment in experimentQL['data']['experiments']['edges']]
        if experiments:
            self.experiments = [self._complete_experiment_graphql(experiment) for experiment in experiments]
            self.logger.debug("Experiment are fetched: %s", self.experiments)
        return experiments

    def obtain_tests(self, site_id: int, per_page=-1) -> List[Dict[str, Any]]:
        """
        :param site_id:
        :param per_page:
        :return: None
        """
        self.logger.debug("Fetching experiments")
        query_values = {'perPage': per_page}
        filters = [
            self._get_filter('siteId', 'EQUAL', [site_id]),
            self._get_filter('status', 'IN', ['ACTIVE', 'DEVIATED']),
            self._get_filter('type', 'IN', ['SERVER_SIDE', 'HYBRID'])
        ]
        experiments = self._fetch_all(f"{self.automation_base_url}experiments",
                                      payload=query_values,
                                      filters=filters,
                                      headers=self._get_headers())
        if experiments:
            self.experiments = [self._complete_experiment(experiment) for experiment in experiments]
            self.logger.debug("Experiment are fetched: %s", self.experiments)
        return experiments

    def obtain_feature_flags_graphql(
        self, site_code: str,
        environment: str = 'production',
        per_page=-1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Obtain feature flags with GraphQL
        :param site_id:
        :param per_page:
        :return: Optional[List[Dict]]
        """
        self.logger.debug("Fetching feature flags")
        feature_flags = self._fetch_all_graphql(f"{self.automation_base_url}v1/graphql?perPage={per_page}",
                                                data=query_ql_feature_flags(site_code, environment),
                                                headers=self._get_headers())
        feature_flags = [feature_flag['node'] for feature_flag_QL in feature_flags
                         for feature_flag in feature_flag_QL['data']['featureFlags']['edges']]
        if feature_flags:
            self.feature_flags = [self._complete_campaign_graphql(feature_flag) for feature_flag in feature_flags]
            self.logger.debug("Feature flags are fetched %s", self.feature_flags)
        return feature_flags

    def obtain_feature_flags(self, site_id: int, per_page=-1) -> Optional[List[Dict[str, Any]]]:
        """

        :param site_id:
        :param per_page:
        :return: Optional[List[Dict]]
        """
        self.logger.debug("Fetching feature flags")
        query_values = {'perPage': per_page}
        filters = [
            self._get_filter('siteId', 'EQUAL', [site_id]),
            self._get_filter('status', 'IN', ['ACTIVE', 'PAUSED'])
        ]
        feature_flags = self._fetch_all(f"{self.automation_base_url}feature-flags",
                                        payload=query_values,
                                        filters=filters,
                                        headers=self._get_headers())
        if feature_flags:
            self.feature_flags = [self._complete_experiment(feature_flag) for feature_flag in feature_flags]
            self.logger.debug("Feature flags are fetched %s", self.feature_flags)
        return feature_flags

    def _get_common_ssx_parameters(self, visitor_code: str) -> Dict[str, str]:
        """
        :param visitor_code:
        :return:
        """
        return {
            'nonce': get_nonce(),
            'siteCode': self.site_code,
            'visitorCode': visitor_code
        }

    def _get_experiment_register_url(self, visitor_code: str, experiment_id: int,
                                     variation_id: Optional[int] = None, none_variation=False) -> str:
        """
        :param visitor_code:
        :param experiment_id:
        :param variation_id:
        :param none_variation:
        :return:
        """
        ssx_parameters = urlencode(self._get_common_ssx_parameters(visitor_code))
        url = f"experimentTracking?{ssx_parameters}&experimentId={experiment_id}"
        if variation_id:
            url += f"&variationId={variation_id}"
        if none_variation:
            url += "&noneVariation=true"
        return url

    def _get_data_register_url(self, visitor_code) -> str:
        """

        :param visitor_code:
        :return:
        """
        return "dataTracking?" + urlencode(self._get_common_ssx_parameters(visitor_code))

    def _get_api_data_request_url(self, key: str) -> str:
        """

        :param key:
        :return:
        """
        params = {
            'siteCode': self.site_code,
            'key': key
        }
        return self.api_data_url + "data?" + urlencode(params)

    def get_feature_flag(self, feature_key: Union[int, str]) -> Dict[str, Any]:
        """

        :param feature_key:
        :return:
        """
        if isinstance(feature_key, str):
            _id = 'identificationKey'
        elif isinstance(feature_key, int):
            _id = 'id'
        else:
            raise TypeError("Feature key should be a String or an Integer.")
        feature_flags = [feature_flag for feature_flag in self.feature_flags if feature_flag[_id] == feature_key]
        feature_flag = None
        if feature_flags:
            feature_flag = feature_flags[0]
        if feature_flag is None:
            raise FeatureConfigurationNotFound(message=feature_key)
        return feature_flag

    def track_experiment(self, visitor_code: str, experiment_id, variation_id=None, none_variation=False) -> None:
        """
        Track experiment
        :param visitor_code:
        :param experiment_id:
        :param variation_id:
        :param none_variation:
        :return: None
        """
        data_not_sent = self._data_not_sent(visitor_code)
        data = data_not_sent.get(visitor_code, [])

        options = {
            "path": self._get_experiment_register_url(visitor_code, experiment_id, variation_id, none_variation),
            "body": ("\n".join([
                data_instance.obtain_full_post_text_line() for data_instance in data]) or "").encode(  # type: ignore
                "UTF-8")
        }
        trial = 0
        self.logger.debug("Start post tracking experiment: %s", data_not_sent)
        success = False
        while trial < 10:
            resp = self.make_sync_request(f"{self.tracking_base_url}{options['path']}",
                                          headers=self._get_headers(), payload=options['body'])
            self.logger.debug("Request %s", resp)
            if resp:
                for data_instance in data:
                    data_instance.sent = True
                trial += 1
                success = True
                break
            trial += 1
        if success:
            self.logger.debug("Post to experiment tracking is done after %s trials", trial)
        else:
            self.logger.error("Post to experiment tracking is not done after %s trials", trial)

    def track_data(self, visitor_code: Optional[str] = None):
        """
        Tracking data
        :param visitor_code: Optional[str]
        :return:
        """
        trials = 10
        data_not_sent = self._data_not_sent(visitor_code)

        self.logger.debug("Start post tracking data: %s", data_not_sent)

        while trials > 0 and data_not_sent:
            for v_code, data_list_instances in data_not_sent.items():
                body = [data_instance.obtain_full_post_text_line() for data_instance in  # type: ignore
                        data_list_instances]
                options = {
                    'path': self._get_data_register_url(v_code),
                    'body': ("\n".join(body)).encode(
                        "UTF-8")
                }
                self.logger.debug("Post tracking data for visitor_code: %s with options: %s", data_list_instances,
                                  options)
                resp = self.make_sync_request(f"{self.tracking_base_url}{options['path']}",
                                              headers=self._get_headers(), payload=options['body'])
                if resp:
                    for data_instance in data_list_instances:
                        data_instance.sent = True
                    data_not_sent = self._data_not_sent(visitor_code)
                    if not data_not_sent:
                        break
                trials -= 1
        self.logger.debug("Post to data tracking is done")

    def _data_not_sent(self, visitor_code: Optional[str] = None) -> Dict[str, List[Type[Data]]]:
        """
        :param visitor_code: Optional[str]
        :return: Dict[str, List[Type[Data]]]
        """
        data = {}
        if visitor_code:
            try:
                data[visitor_code] = [
                    data_instance
                    for data_instance in self.data[visitor_code] if not data_instance.sent
                ]
                if not data[visitor_code]:
                    data = {}
            except (KeyError, IndexError) as ex:
                self.logger.error(ex)
        else:
            for vis_code, data_list in self.data.items():
                if data_list:
                    data[vis_code] = [data_instance for data_instance in data_list if not data_instance.sent]
        return data

    def _check_site_code_enable(self, exp_or_ff: Dict[str, Any]):
        """
        raise SiteCodeDisabled if site of Experiment or Feature Flag is disabled
        :param exp_or_ff:
        :type exp_or_ff: Dict[str, Any]
        """
        if exp_or_ff.get('site') is not None and not exp_or_ff['site']['isKameleoonEnabled']:
            raise SiteCodeDisabled(self.site_code)

    def _check_feature_key(self, feature_key: Union[str, int]):
        """
        warning user that feature_id is deprecated and need to pass feature_key with `str` type
        :param feature_key:
        :type feature_key: Union[str, int]
        """
        if isinstance(feature_key, int):
            warnings.warn(
                'Passing `feature_key` with type of `int` to `activate_feature` or `obtain_feature_variable` '
                'is deprecated, it will be removed in next releases. This is necessary to support multi-environment '
                'feature')

    def _setup_client_configuration(self,
                                    configuration_path: str,
                                    configuration_object: Optional[KameleoonClientConfiguration]):
        """
        helper method to parse client configuration and setup client
        """
        config_yml = configuration_path or DEFAULT_CONFIGURATION_PATH
        self.config = config(config_yml, configuration_object)
        try:
            target_environment = self.config['target_environment']
        except KeyError:
            target_environment = 'prod'
        if target_environment == 'test':
            self.tracking_base_url = "https://api-ssx.kameleoon.net/"
        else:
            self.tracking_base_url = "https://api-ssx.kameleoon.com/"
        try:
            self.environment = self.config['environment']
        except KeyError:
            self.environment = 'production'
        try:
            self.multi_threading = self.config['multi_threading']
        except KeyError:
            self.multi_threading = False
        try:
            actions_configuration_refresh_interval = int(self.config['actions_configuration_refresh_interval'])
            self.actions_configuration_refresh_interval = actions_configuration_refresh_interval * 60
        except KeyError:
            self.actions_configuration_refresh_interval = DEFAULT_CONFIGURATION_UPDATE_INTERVAL

    def _run_in_threads_if_needed(self,
                                  multi_threading: bool,
                                  func,
                                  args: List[Any],
                                  thread_name: str):
        """
        it's wrapper function which run the `func`
        in another thread if multi_threading option is True
        else it calls the `func` in the same thread
        :param multi_threading: Flag to determine if run in multi-threading
        :type multi_threading: Boolean
        :param func: Function need to be called
        :type func: Function
        :param args: List of arguments for `func`
        :type args: List[Any]
        :param thread_name: Name of thread if `func` runs
        in another thread
        :type args: str
        """
        if multi_threading:
            thread = threading.Thread(target=func, args=args)
            thread.daemon = True
            thread.setName(thread_name)
            thread.start()
        else:
            func(*args)
