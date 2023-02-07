import os
from unittest import TestCase
from pathlib import Path
import json
from unittest import mock
from main import send_weather_request, current_datetimes

from main import mocked_weather_request_get

"""The Test Case Class"""
class TestCurrentDateTime(TestCase):

    """ Tests for the weather request calls """

    """ This tests if a random city (Chicago), mocking the weather url, returns the same mock response as our weather_request functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_send_weather_request_chicago(self, mock_get):
        chicago_response = send_weather_request("dummy-weather-url","dummy-weather-key","Chicago,IL")
        self.assertTrue(chicago_response == "2023-02-07 01:19")

    """ This tests if a random city (New Delhi), mocking the weather url, returns the same mock response as our weather_request functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_send_weather_request_new_delhi(self, mock_get):
        delhi_response = send_weather_request("dummy-weather-url", "dummy-weather-key", "New Delhi,India")
        self.assertTrue(delhi_response == "2023-02-07 12:50")

    """ This tests if an invalid city, mocking the weather url, returns the same mock response as our weather_request functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_send_weather_request_unknown(self, mock_get):
        error_response = send_weather_request("dummy-weather-url", "dummy-weather-key", "SomePlace,SomeCountry")
        self.assertTrue(error_response == "Failed to fetch")

    """ Tests for the actual current_datetimes functions """

    """ This test our actual cloud functions (current_datetimes) with 2 valid cities, mocking the weather url, returns the same mock response as our cloud functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_current_datetimes_chicago_and_new_delhi(self, mock_get):
        os.environ["WEATHER_URL"] = "dummy-weather-url"
        os.environ["WEATHER_URL"] = "dummy-weather-key"
        args = {"city1": "Chicago,IL", "city2": "New Delhi,India"}
        request = MockRequest(args)
        response = current_datetimes(request)
        actual_response = None
        count = 0
        for i in response:
            if count == 0:
                actual_response = i
                break
        actual_response = json.loads(actual_response)
        date = actual_response[0]["date"]
        # Assert Chicage time matched
        chicago_date = date["Chicago,IL"]
        path = Path(__file__) / "../test_files/chicago.json"
        with path.open() as f:
            data = json.load(f)
            date = data["data"]
            time_zone = date["time_zone"]
            localtime = time_zone[0]["localtime"]
            self.assertTrue(chicago_date == localtime)
        # Assert New Delhi time matched
        date = actual_response[0]["date"]
        delhi_date = date["New Delhi,India"]
        path = Path(__file__) / "../test_files/new_delhi.json"
        with path.open() as f:
            data = json.load(f)
            date = data["data"]
            time_zone = date["time_zone"]
            localtime = time_zone[0]["localtime"]
            self.assertTrue(delhi_date == localtime)

    """ This test our actual cloud functions (current_datetimes) with 1 valid city and 1 invalid city, mocking the weather url, returns the same mock response as our cloud functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_current_datetimes_chicago_and_invalid_city(self, mock_get):
        os.environ["WEATHER_URL"] = "dummy-weather-url"
        os.environ["WEATHER_URL"] = "dummy-weather-key"
        args = {"city1": "Chicago,IL", "city2": "Some City,Some Country"}
        request = MockRequest(args)
        response = current_datetimes(request)
        actual_response = None
        count = 0
        for i in response:
            if count == 0:
                actual_response = i
                break
        actual_response = json.loads(actual_response)
        date = actual_response[0]["date"]
        # Assert Chicage time matched
        chicago_date = date["Chicago,IL"]
        path = Path(__file__) / "../test_files/chicago.json"
        with path.open() as f:
            data = json.load(f)
            date = data["data"]
            time_zone = date["time_zone"]
            localtime = time_zone[0]["localtime"]
            self.assertTrue(chicago_date == localtime)
        # Assert New Delhi time matched
        date = actual_response[0]["date"]
        delhi_date = date["Some City,Some Country"]
        self.assertTrue(delhi_date == "Failed to fetch")

    """ This test our actual cloud functions (current_datetimes) with invalid input (1 city missing in request), mocking the weather url, returns the same mock response as our cloud functions"""
    @mock.patch('requests.get', side_effect=mocked_weather_request_get)
    def test_current_datetimes_invalid_input(self, mock_get):
        os.environ["WEATHER_URL"] = "dummy-weather-url"
        os.environ["WEATHER_URL"] = "dummy-weather-key"
        args = {"city1": "Chicago,IL"}
        request = MockRequest(args)
        response = current_datetimes(request)
        print(f"{response}")
        count = 0
        actual_response = None
        actual_status = 200
        for i in response:
            if count == 0:
                actual_response = i
            if count == 1:
                actual_status = i
            count += 1
        self.assertTrue(actual_response == "{\"error\": \"Can't process, city1 and city2 are required parameters\"}")
        self.assertTrue(actual_status == 400)

"""Mock Http Request"""
class MockRequest():

    def __init__(self, args) -> None:
        self.args = args


