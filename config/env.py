import os


class Env():
  def get(key: str):
    return os.environ.get(key)

  def getApiUrl():
    return Env.get("TRANSLATION_API_URL")

  def getSecretKey():
    return Env.get("SECRET_KEY")

  def isMockEnabled():
    return Env.get("MOCK") == "True"

  def getRootDir():
    return Env.get("TRANSLATION_ROOT_DIR")
