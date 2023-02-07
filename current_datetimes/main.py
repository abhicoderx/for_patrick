from pathlib import Path

import functions_framework
import requests
import os
import json

"""The HTTP Cloud Function
  """
@functions_framework.http
def current_datetimes(request):
   # The HTTP Request
   request_args = request.args
   # Parse tje query params
   city1 = request_args.get("city1")
   city2 = request_args.get("city2")
   # Error if not both cities passed
   if not city1 or not city2:
      return json.dumps({"error":"Can't process, city1 and city2 are required parameters"}), 400, {'Content-Type': 'application/json'}
   # Weather URL and Key from env
   weather_url = os.environ.get('WEATHER_URL')
   weather_key =  os.environ.get('WEATHER_KEY')
   # Response data structures
   response_arr = []
   response_json = {}
   # Get localtime for city1
   city1_resp = send_weather_request(weather_url, weather_key, city1)
   # Get localtime for city2
   city2_resp = send_weather_request(weather_url, weather_key, city2)
   # Format the response
   tzs_json = {}
   tzs_json[city1] = city1_resp
   tzs_json[city2] = city2_resp
   response_json["date"] = tzs_json
   response_arr.append(response_json)
   # Send the response
   return json.dumps(response_arr), 200, {'Content-Type': 'application/json'}

"""Utility function to make http get to weather URL
  """
def send_weather_request(weather_url,weather_key, city):
   # Create the URL
   city_url = weather_url + f"?q={city}&format=json&key={weather_key}"
   city_response = requests.get(city_url)
   weather_rsp_json = city_response.json()
   # Error on error from the api
   if city_response.status_code != 200 or "error" in weather_rsp_json["data"]:
      return "Failed to fetch"
   else:
      # Parse localtime from the response and return
      tz = weather_rsp_json["data"]["time_zone"]
      zeroeth = tz[0]
      localtime = zeroeth["localtime"]
      return localtime

"""This method will be used by the mock to replace requests.get
  """
def mocked_weather_request_get(*args, **kwargs):
  class MockResponse:
      def __init__(self, json_data, status_code):
          self.json_data = json_data
          self.status_code = status_code

      def json(self):
          return self.json_data
  if 'Chicago' in args[0] :
      path = Path(__file__) / "../tests/test_files/chicago.json"
      with path.open() as f:
          data = json.load(f)
      return MockResponse(data, 200)
  elif 'New Delhi' in args[0]:
      path = Path(__file__) / "../tests/test_files/new_delhi.json"
      with path.open() as f:
          data = json.load(f)
      return MockResponse(data, 200)
  else:
      path = Path(__file__) / "../tests/test_files/error.json"
      with path.open() as f:
          data = json.load(f)
      return MockResponse(data, 200)