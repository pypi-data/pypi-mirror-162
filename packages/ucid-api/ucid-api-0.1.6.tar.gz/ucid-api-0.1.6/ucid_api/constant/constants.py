class RequestPath:
    SUBMIT = '/submit'
    RESULT = '/results'
    DETAILS = '/details'
    NUMBER = '/number'
    GENERATE = '/generate'
    UPDATE = '/update'


class Constants:
    AUTHORIZATION = 'Authorization'
    AUTHENTICATION_TOKEN = 'Authentication-Token'
    UCID_API_URL = 'https://ucid-stage.pntrzz.com/ucid'
    RETRY_AFTER_STATUS_CODES = (500, 502, 504)
    SUCCESS_STATUS_CODES = (200, 202, 201)
    CONNECTION_TIMEOUT = 5

