'''
Created on September 20, 2021
@author: lwoydziak
'''
from json import loads

from mockito.matchers import any, Contains, And, ArgThat, Eq
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


def test_viewJourneyAdded():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journey', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'result': 'success'})
    Xenon().event({'category': 'Event1', 'action': 'test'})
    Xenon().commit(PostMethod=requests.post, sleepTime=0, verify=False)

    def matchesJourneyApiParameters(arg):
        apiArguments = loads(arg)
        parameters = apiArguments['parameters']
        assert Eq("ApiJourney").matches(apiArguments['name'])
        assert Eq('Event1').matches(parameters['journey'][0]['category'])
        assert any(float).matches(parameters['journey'][0]['timestamp'])
        assert any(str).matches(parameters['uuid'])
        assert any(float).matches(parameters['timestamp'])
        return True

    verify(requests).post('https://<apiUrl>/journey',
                          data=ArgThat(matchesJourneyApiParameters),
                          headers={'Authorization': 'Bearer <apiKey>'},
                          verify=False)
    assert Xenon().journey() == []


def test_viewJourneyFailsWithOneSslError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journey', data=any(), headers=any(), verify=False).thenRaise(
        SSLError).thenReturn(response)
    when(response).json().thenReturn({'result': 'success'})
    Xenon().event({'category': 'Event1', 'action': 'test'})
    Xenon().commit(PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/journey',
                                   data=And([Contains('{"name": "ApiJourney", "parameters": '),
                                             Contains('{"journey": [{"category": "Event1", "action": "test", "timestamp":'),
                                             Contains('}], "uuid":')]),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)
    assert Xenon().journey() == []


def test_viewJourneyFailsWithOneError():
    requests = mock()
    response = mock()
    response.status_code = 200
    when(requests).post('https://<apiUrl>/journey', data=any(), headers=any(), verify=False).thenRaise(
        Exception).thenReturn(response)
    when(response).json().thenReturn({'result': 'success'})
    Xenon().event({'category': 'Event1', 'action': 'test'})
    Xenon().commit(PostMethod=requests.post, sleepTime=0, verify=False)
    verify(requests, times=2).post('https://<apiUrl>/journey',
                                   data=And([Contains('{"name": "ApiJourney", "parameters": '),
                                             Contains('{"journey": [{"category": "Event1", "action": "test", "timestamp":'),
                                             Contains('}], "uuid":')]),
                                   headers={'Authorization': 'Bearer <apiKey>'},
                                   verify=False)
    assert Xenon().journey() == []


def test_viewJourneyFails():
    requests = mock()
    response = mock()
    response.status_code = 400
    when(requests).post('https://<apiUrl>/journey', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'result': 'failed'})
    with raises(ApiException) as e:
        Xenon().event({'category': 'Event1', 'action': 'test'})
        Xenon().commit(PostMethod=requests.post, sleepTime=0, verify=False)

    assert Contains('Api responded with error.').matches(str(e.exconly()))
    journey = Xenon().journey()[0]
    assert journey['action'] == 'test'
    assert journey['timestamp'] > 0.0


def test_WhenViewJourneyFailsExceptionContainsResponse():
    requests = mock()
    response = mock()
    response.status_code = 400
    when(requests).post('https://<apiUrl>/journey', data=any(), headers=any(), verify=False).thenReturn(response)
    when(response).json().thenReturn({'result': 'failed'})
    try:
        Xenon().event({'step': 'step1'})
        Xenon().commit(PostMethod=requests.post, sleepTime=0, verify=False)
    except ApiException as e:
        assert e.apiResponse().status_code == response.status_code
