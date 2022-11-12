from request import post_request
from config.env import Env
from typing import List
import mockApi


def transform_result(api_response):
  try:
    return api_response["data"]["translations"]
  except (KeyError, TypeError) as e:
    return []


def get_translations_for(messages: List[str], targetLanguage: str):
  body = {
      "q": messages,
      "target": targetLanguage
  }
  params = {"key": Env.get_secret_key()}
  result = []
  if Env.is_mock_enabled():
    result = mockApi.get_dummy_response(len(messages))
  else:
    result = post_request(Env.get_api_url(), params=params, postData=body)
  return transform_result(result), result
