import requests
from config.env import Env


def postRequest(url: str, params={}, postData={}, options={}):
  response = requests.post(url, params=params, data=postData)
  return response.json()


def getRequest(url: str, params={}, options={}):
  response = requests.post(url, params=params)
  return response.json()
