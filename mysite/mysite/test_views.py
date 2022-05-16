import pytest
import json
from decouple import config
import os

# def test_segmentize():
#     from mysite.views import segmentize
#     website_text = '''
#     This is a test sentence.
#     This is another test sentence.
#     This is a third test sentence.
#     '''
#     MAX_CHAR_COUNT = 10
#     MAX_SEGMENT_COUNT = 20
#     segments_of_website = segmentize(website_text, MAX_CHAR_COUNT, MAX_SEGMENT_COUNT)
#     print("segments of website:", segments_of_website)
#     assert len(segments_of_website) == 3
#     assert segments_of_website[0] == 'This is a test sentence.'
#     assert segments_of_website[1] == 'This is another test sentence.'
#     assert segments_of_website[2] == 'This is a third test sentence.'

def test_json_loads():
    json_from_client = json.loads('{"body": "hello", "apiKey": "asdf", "test": false}')
    api_key_list_string = config('VALID_API_KEY_LIST')
    api_key_list = json.loads(api_key_list_string)
    assert json_from_client['apiKey'] not in api_key_list
    assert json_from_client['test'] is False
    assert json_from_client['body'] == "hello"


def test_json_loads2():
    json_from_client = json.loads('{"body": "hi my name is", "apiKey": "this shouldnt pass", "test": true}')
    api_key_list_string = config('VALID_API_KEY_LIST')
    api_key_list = json.loads(api_key_list_string)
    assert json_from_client['apiKey'] not in api_key_list
    assert json_from_client['test'] is True
    assert json_from_client['body'] == "hi my name is"

def test_json_loads_valid_api_key():
    json_from_client = json.loads('{"body": "dummy body", "apiKey": "this shouldnt pass", "test": false}')
    json_from_client['apiKey'] = config('VALID_TEST_API_KEY')
    api_key_list_string = config('VALID_API_KEY_LIST')
    api_key_list = json.loads(api_key_list_string)
    assert json_from_client['apiKey'] in api_key_list
    assert json_from_client['test'] is False
    assert json_from_client['body'] == "dummy body"