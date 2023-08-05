import json

from ucid_api.utils.utils import requests_retry_session
from ucid_api.constant.constants import RequestPath
from ucid_api.constant.constants import Constants
from ucid_api.utils.header_validate import HeaderValidate


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

        if len(self.__token.split(' ')) == 2:
            self.__headers[Constants.AUTHORIZATION] = self.__token
        else:
            self.__headers[Constants.AUTHENTICATION_TOKEN] = self.__token

        response = requests_retry_session().post(
            url=final_url,
            headers=self.__headers,
            timeout=5,
            json=_payload,
        )

        if response.status_code not in [200, 202, 201]:
            raise Exception('failed to get ucid details to header : {}, payload : {}, url:{}, response_code:{}'.format(
                json.dumps(self.__headers, indent=2), json.dumps(_payload, indent=2),
                final_url, response.status_code))
        return response.text
