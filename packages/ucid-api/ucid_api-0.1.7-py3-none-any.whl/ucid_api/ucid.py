import json

from ucid_api.utils.utils import requests_retry_session
from ucid_api.constant.constants import RequestPath
from ucid_api.constant.constants import Constants
from ucid_api.utils.header_validate import HeaderValidate
from ucid_api.exception.ucid_exception import UcidError


class Ucid:
    """
    Instantiate an ucid api gateway
    """

    def __init__(self, _headers, _token):
        self.__headers = _headers
        self.__token = _token
        HeaderValidate().validate_headers(self.__headers)

    def submit(self, _payload):
        return Ucid.__call_ucid(self, _payload, RequestPath.SUBMIT)

    def details(self, _payload):
        Ucid.__call_ucid(self, _payload, RequestPath.DETAILS)

    def number(self, _payload):
        return Ucid.__call_ucid(self, _payload, RequestPath.NUMBER)

    def generate(self, _payload):
        return Ucid.__call_ucid(self, _payload, RequestPath.GENERATE)
        pass

    def update(self, _payload):
        Ucid.__call_ucid(self, _payload, RequestPath.UPDATE)
        pass

    def result(self, _payload):
        Ucid.__call_ucid(self, _payload, RequestPath.RESULT)
        pass

    def __call_ucid(self, _payload, request_path):

        final_url = Constants.UCID_API_URL + request_path
        try:
            if len(self.__token.split(' ')) == 2:
                self.__headers[Constants.AUTHORIZATION] = self.__token
            else:
                self.__headers[Constants.AUTHENTICATION_TOKEN] = self.__token

            response = requests_retry_session().post(
                url=final_url,
                headers=self.__headers,
                timeout=Constants.CONNECTION_TIMEOUT,
                json=_payload,
            )
        except Exception as ex:
            raise UcidError(ex)
        return response
