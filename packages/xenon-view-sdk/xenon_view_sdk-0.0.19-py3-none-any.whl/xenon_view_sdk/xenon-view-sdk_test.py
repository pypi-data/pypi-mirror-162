'''
Created on September 20, 2021
@author: lwoydziak
'''
from mockito.matchers import Contains
from pytest import raises

from xenon_view_sdk import Xenon


def setup_function(function):
    Xenon._instance = None


def teardown_function(function):
    Xenon._instance = None


def test_cannotCreateView():
    with raises(ValueError) as e:
        Xenon()
    assert Contains('Xenon should be initialized with an API Key from XenonView.').matches(str(e.exconly()))


def test_canChangeViewApiKey():
    Xenon(apiKey='<API KEY>', apiUrl='<url>')
    newApiKey = 'new'
    Xenon().key(newApiKey)
    assert newApiKey == Xenon().key()


def test_canAddPageView():
    Xenon(apiKey='<API KEY>')
    Xenon().pageView("mine")
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Page View'
    assert journey['action'] == 'mine'
    assert journey['timestamp'] > 0.0


def test_canAddOutcome():
    Xenon(apiKey='<API KEY>')
    Xenon().outcome("<my outcome>", "<action>")
    journey = Xenon().journey()[0]
    assert journey['outcome'] == '<my outcome>'
    assert journey['action'] == '<action>'
    assert journey['timestamp'] > 0.0


def test_canAddOutcomeWithPlatformReset():
    Xenon(apiKey='<API KEY>')
    softwareVersion = "5.1.5"
    deviceModel = "Pixel 4 XL"
    operatingSystemVersion = "Android 12.0"
    Xenon().platform(softwareVersion, deviceModel, operatingSystemVersion)
    Xenon().removePlatform()
    Xenon().outcome("<my outcome>", "<action>")
    journey = Xenon().journey()[0]
    assert journey['outcome'] == '<my outcome>'
    assert journey['action'] == '<action>'
    assert journey['timestamp'] > 0.0


def test_canAddOutcomeWithPlatform():
    Xenon(apiKey='<API KEY>')
    softwareVersion = "5.1.5"
    deviceModel = "Pixel 4 XL"
    operatingSystemVersion = "Android 12.0"
    Xenon().platform(softwareVersion, deviceModel, operatingSystemVersion)
    Xenon().outcome("<my outcome>", "<action>")
    journey = Xenon().journey()[0]
    assert journey['outcome'] == '<my outcome>'
    assert journey['action'] == '<action>'
    assert journey['platform'] == {
        "softwareVersion": softwareVersion,
        "deviceModel": deviceModel,
        "operatingSystemVersion": operatingSystemVersion
    }
    assert journey['timestamp'] > 0.0


def test_canAddFunnel():
    Xenon(apiKey='<API KEY>')
    Xenon().funnel("<my step in funnel>", "<action>")
    journey = Xenon().journey()[0]
    assert journey['funnel'] == '<my step in funnel>'
    assert journey['action'] == '<action>'
    assert journey['timestamp'] > 0.0


def test_doesNotAddDuplicateEvent():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'category': 'Event1', 'action': 'test'})
    Xenon().event({'category': 'Event1', 'action': 'test'})
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event1'
    assert journey['timestamp'] > 0.0
    assert journey['count'] == 2
    assert len(Xenon().journey()) == 1


def test_addSecondEvent():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'category': 'Event1', 'action': 'test1'})
    Xenon().event({'category': 'Event2', 'action': 'test2', 'extra': 'value'})
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event1'
    assert journey['timestamp'] > 0.0
    journey = Xenon().journey()[1]
    assert journey['category'] == 'Event2'
    assert journey['timestamp'] > 0.0


def test_addEventAndOutcome():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'category': 'Event1', 'action': 'test1'})
    Xenon().outcome('Event2', 'test2')
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event1'
    assert journey['timestamp'] > 0.0
    journey = Xenon().journey()[1]
    assert journey['outcome'] == 'Event2'
    assert journey['timestamp'] > 0.0


def test_addCustomEvent():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'custom': 'test'})
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event'
    assert journey['action'] == {'custom': 'test'}
    assert journey['timestamp'] > 0.0


def test_addGenericEvent():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'action': 'test'})
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event'
    assert journey['action'] == 'test'
    assert journey['timestamp'] > 0.0


def test_addSecondPageView():
    Xenon(apiKey='<API KEY>')
    Xenon().pageView('p1')
    Xenon().pageView('p2')

    journey = Xenon().journey()[0]
    assert journey['category'] == 'Page View'
    assert journey['action'] == 'p1'
    assert journey['timestamp'] > 0.0
    journey = Xenon().journey()[1]
    assert journey['category'] == 'Page View'
    assert journey['action'] == 'p2'
    assert journey['timestamp'] > 0.0


def test_whenResetingAddingEventAndRestoringRestoredJourneyHasNewEvent():
    Xenon(apiKey='<API KEY>')
    Xenon().event({'category': 'Event1', 'action': 'test'})
    Xenon().reset()
    Xenon().event({'category': 'Event2', 'action': 'test2'})
    Xenon().restore()
    journey = Xenon().journey()[0]
    assert journey['category'] == 'Event1'
    assert journey['timestamp'] > 0.0
    journey = Xenon().journey()[1]
    assert journey['category'] == 'Event2'
    assert journey['timestamp'] > 0.0


def test_canGetAndSetId():
    Xenon(apiKey='<API KEY>')
    assert Xenon().id() != None and Xenon().id() != ''
    Xenon().id('test')
    assert Xenon().id() == 'test'


def test_canRegenerateId():
    Xenon(apiKey='<API KEY>')
    previousId = Xenon().id()
    Xenon().newId()
    assert Xenon().id() != previousId
