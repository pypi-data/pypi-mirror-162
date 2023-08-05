import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def requests_retry_session(retries=3, backoff_factor=0.3, session=None,
                           status_forcelist=(500, 502, 504)):
    '''
    Source: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    '''
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
