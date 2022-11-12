import requests
from config.env import Env


def post_request(url: str, params={}, postData={}, options={}):
  response = requests.post(url, params=params, data=postData)
  return response.json()


def get_request(url: str, params={}, options={}):
  response = requests.post(url, params=params)
  return response.json()
