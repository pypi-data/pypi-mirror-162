'''
Created on September 20, 2021
@author: lwoydziak
'''
from mockito.matchers import any, Contains
from mockito.mocking import mock
from mockito.mockito import verify, when
from pytest import raises
from requests.exceptions import SSLError

from xenon_view_sdk import Xenon, ApiException

apiKey = '<apiKey>'
apiUrl = '<apiUrl>'


def setup_function(function):
    Xenon(apiKey=apiKey, apiUrl=apiUrl)


def teardown_function(function):
    Xenon._instance = None


def test_ApiGetJourneys():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journeys', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'journeys': []})
    Xenon().journeys(PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests).post('https://<apiUrl>/journeys',
                          data=Contains('{"name": "ApiJourneys", "parameters": {"uuid":'),
                          headers={'Authorization': 'Bearer <apiKey>'},
                          verify=False)


def test_ApiGetJourneysWithOneSslError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journeys', data=any(), headers=any(), verify=False).thenRaise(
        SSLError).thenReturn(response)
    when(response).json().thenReturn({'journeys': []})
    Xenon().journeys(PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/journeys',
                                   data=Contains('{"name": "ApiJourneys", "parameters": {"uuid":'),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)


def test_ApiGetJourneysWithOneError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journeys', data=any(), headers=any(), verify=False).thenRaise(
        Exception).thenReturn(response)
    when(response).json().thenReturn({'journeys': []})
    Xenon().journeys(PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/journeys',
                                   data=Contains('{"name": "ApiJourneys", "parameters": {"uuid":'),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)


def test_ApiGetJourneysFails():
    requests = mock()
    response = mock()
    response.status_code = 400
    when(requests).post('https://<apiUrl>/journeys', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'result': 'failed'})
    with raises(ApiException) as e:
        Xenon().journeys(PostMethod=requests.post, sleepTime=0, verify=False)

    assert Contains('Api responded with error.').matches(str(e.exconly()))
