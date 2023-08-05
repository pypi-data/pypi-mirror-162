'''
Created on October 22, 2021
@author: lwoydziak
'''
from mockito.matchers import any, Contains, And
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


def test_ApiDeanonymize():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/deanonymize', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'deanonymize': []})
    Xenon().deanonymize("test", PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests).post('https://<apiUrl>/deanonymize',
                          data=And([Contains('{"name": "ApiDeanonymize", "parameters": {'),
                                    Contains('"person": "test",'),
                                    Contains('"timestamp":'),
                                    Contains('"uuid":')]),
                          headers={'Authorization': 'Bearer <apiKey>'},
                          verify=False)


def test_ApiDeanonymizeWithOneSslError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/deanonymize', data=any(), headers=any(), verify=False).thenRaise(
        SSLError).thenReturn(response)
    when(response).json().thenReturn({'deanonymize': []})
    Xenon().deanonymize("test", PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/deanonymize',
                                   data=And([Contains('{"name": "ApiDeanonymize", "parameters": {'),
                                             Contains('"person": "test",'),
                                             Contains('"timestamp":'),
                                             Contains('"uuid":')]),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)


def test_ApiDeanonymizeWithOneError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/deanonymize', data=any(), headers=any(), verify=False).thenRaise(
        Exception).thenReturn(response)
    when(response).json().thenReturn({'deanonymize': []})
    Xenon().deanonymize("test", PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/deanonymize',
                                   data=And([Contains('{"name": "ApiDeanonymize", "parameters": {'),
                                             Contains('"person": "test",'),
                                             Contains('"timestamp":'),
                                             Contains('"uuid":')]),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)


def test_ApiDeanonymizeFails():
    requests = mock()
    response = mock()
    response.status_code = 400
    when(requests).post('https://<apiUrl>/deanonymize', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'result': 'failed'})
    with raises(ApiException) as e:
        Xenon().deanonymize("test", PostMethod=requests.post, sleepTime=0, verify=False)

    assert Contains('Api responded with error.').matches(str(e.exconly()))
