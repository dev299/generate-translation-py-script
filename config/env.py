import os


class Env():
  def get(key: str):
    return os.environ.get(key)

  def get_api_url():
    return Env.get("TRANSLATION_API_URL")

  def get_secret_key():
    return Env.get("SECRET_KEY")

  def is_mock_enabled():
    return Env.get("MOCK") == "True"

  def get_root_dir():
    return Env.get("TRANSLATION_ROOT_DIR")

  def get_batch_size():
    return int(Env.get("BATCH_SIZE"))
