from request import postRequest
from config.env import Env
from typing import List
import mockApi


def getTranslationsFor(messages: List[str], targetLanguage: str):
  body = {
      "q": messages,
      "target": targetLanguage
  }
  params = {"key": Env.getSecretKey()}
  if Env.isMockEnabled():
    return mockApi.getDummyResponse(len(messages))

  return postRequest(Env.getApiUrl(), params=params, postData=body)
