import argparse
import re
import math

from dotenv import load_dotenv
from config.env import Env
from api import get_translations_for
from typing import List, Dict
from fileutil import load_json, write_json
load_dotenv()

BATCH_SIZE = Env.get_batch_size()
LOCK_FILE_PREFIX = re.sub("\W", "-", Env.get_root_dir())+"-"


def load_default_translation():
  return load_json(f"{Env.get_root_dir()}/en.json")


def get_keys(allKeys: List[str], languageKey: str):
  filename = get_lock_filename(languageKey)
  final_keys: List[str] = []
  try:
    translated_map: Dict = load_json(filename)
  except FileNotFoundError as e:
    write_json(filename, {})
    return allKeys
  else:
    for key in allKeys:
      if not translated_map.get(key, None):
        final_keys.append(key)

  return final_keys


def get_lock_filename(languageKey):
  return f".lock/{LOCK_FILE_PREFIX}" + languageKey + ".mo"


def update_lock_file(successKeys, languageKey):
  filename = get_lock_filename(languageKey)
  lockMap: Dict = load_json(filename)
  for key in successKeys:
    lockMap.update({key: 1})
  write_json(filename, lockMap)


def update_translation_file(apiResponse, keys, languageKey, retried=False):
  filename = get_translation_filename(languageKey)
  try:
    translation: Dict = {}
    translation = load_json(filename)
    for index, obj in enumerate(apiResponse):
      translated_text = obj["translatedText"]
      translation.update({keys[index]: translated_text})
    write_json(filename, translation, indent=2, ensure_ascii=False)
  except FileNotFoundError as e:
    if not retried:
      write_json(filename, {})
      update_translation_file(apiResponse, keys, languageKey, retried=True)
    else:
      print("Oops there was some error creating the file", e)


def get_translation_filename(languageKey):
  return f"{Env.get_root_dir()}/"+languageKey+".json"


def are_valid_languages(targetLangs: List[str]):
  jsonMap: Dict = load_json("valid_languages.json")
  supported_languages = list(
      map(lambda x: x.get("language"), jsonMap["data"]["languages"]))
  return set(targetLangs).issubset(set(supported_languages))


def run(target: List[str] = None, verbose=False):
  if "en" in target:
    print("You can not use 'en' as target language")
    target.remove("en")
    if len(target) < 1:
      return
  if not are_valid_languages(target):
    print("Given targets does not seems to be a valid language")
    return
  if verbose:
    print("Target languages", target)
    print("Loading default translation file i.e 'en.json'")
  map: dict = load_default_translation()
  if map is not None:
    all_keys = list(map.keys())
    if verbose:
      print(f"Total keys defined in default translation file {len(all_keys)}")

    for languageKey in target:
      if verbose:
        print("=" * 80)
        print(f"Checking keys to be translated for language {languageKey}")
      final_keys = get_keys(all_keys, languageKey)
      l = len(final_keys)
      if l > 0:
        if verbose:
          print(f"{len(final_keys)} keys to be translated for language {languageKey}")
          print(f"Creating batch of {BATCH_SIZE} keys")
        pages = math.ceil(l/BATCH_SIZE)
        for p in range(0, pages):
          batch_keys = final_keys[p * BATCH_SIZE: p * BATCH_SIZE + BATCH_SIZE]
          batch_values = [map[i] for i in batch_keys]
          result, raw_response = get_translations_for(
              batch_values, languageKey)
          if not result:
            print("\nError: Api did not return results as expected\n", raw_response)
            return
          if verbose:
            print("Translation Api Response Success")
          update_translation_file(result, batch_keys, languageKey)
          if verbose:
            print(f"'{languageKey}' translation file updated")
          update_lock_file(batch_keys, languageKey)
          if verbose:
            print(f"Lock file of '{languageKey}' language updated")

      else:
        print(
            f"All keys have been already translated for language '{languageKey}'")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog="Automated Translation Script",
                                   description="Make google api call to translate the english text into various locale")
  parser.add_argument("-t", "--targetLanguages",
                      required=True, dest="target", type=str)
  parser.add_argument("-v", "--verbose", action="store_true")
  args = parser.parse_args()
  try:
    run(target=str(args.target).split(sep=","), verbose=args.verbose)
  except Exception as e:
    print(e.with_traceback())
