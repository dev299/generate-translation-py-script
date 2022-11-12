import argparse
import re
import math

from dotenv import load_dotenv
from config.env import Env
from api import getTranslationsFor
from typing import List, Dict
from fileutil import readFile, writeFile
load_dotenv()

BATCH_SIZE = 20
LOCK_FILE_PREFIX = re.sub("\W", "-", Env.getRootDir())+"-"


def loadDefaultI18n():
  return readFile(f"{Env.getRootDir()}/en.json")


def getKeys(allKeys: List[str], languageKey: str):
  filename = f".lock/{LOCK_FILE_PREFIX}" + languageKey + ".mo"
  final_keys: List[str] = []
  try:
    translatedMap: Dict = readFile(filename)
  except FileNotFoundError as e:
    writeFile(filename, {})
    return allKeys
  else:
    for key in allKeys:
      if not translatedMap.get(key, None):
        final_keys.append(key)

  return final_keys


def updateLockFile(successKeys, languageKey):
  filename = f".lock/{LOCK_FILE_PREFIX}" + languageKey + ".mo"
  lockMap: Dict = readFile(filename)
  for key in successKeys:
    lockMap.update({key: 1})

  writeFile(filename, lockMap)


def updateTranslationFile(apiResponse, keys, languageKey, retried=False):
  filename = f"{Env.getRootDir()}/"+languageKey+".json"
  try:
    translation: Dict = {}
    translation = readFile(filename)
    responseArray = apiResponse["data"]["translations"]
    for index, obj in enumerate(responseArray):
      translated_text = obj["translatedText"]
      translation.update({keys[index]: translated_text})
    writeFile(filename, translation, indent=2, ensure_ascii=False)
  except FileNotFoundError as e:
    if not retried:
      writeFile(filename, {})
      updateTranslationFile(apiResponse, keys, languageKey, retried=True)
    else:
      print("Oops there was some error creating the file", e)


def validLanguages(targetLangs: List[str]):
  jsonMap: Dict = readFile("valid_languages.json")
  validLanguages = list(
      map(lambda x: x.get("language"), jsonMap["data"]["languages"]))
  return set(targetLangs).issubset(set(validLanguages))


def run(target: List[str] = None, verbose=False):
  if "en" in target:
    print("You can not use 'en' as target language")
    target.remove("en")
    if len(target) < 1:
      return
  if not validLanguages(target):
    print("Given targets does not seems to be a valid language")
    return
  if verbose:
    print("Target languages", target)
    print("Loading default translation file i.e 'en.json'")
  map: dict = loadDefaultI18n()
  if map is not None:
    all_keys = list(map.keys())
    if verbose:
      print(f"Total keys defined in default translation file {len(all_keys)}")

    for languageKey in target:
      print("="*80)
      print(f"Checking keys to be translated for language {languageKey}")
      final_keys = getKeys(all_keys, languageKey)
      l = len(final_keys)
      if l > 0:
        if verbose:
          print(f"{len(final_keys)} keys to be translated for language {languageKey}")
          print(f"Creating batch of {BATCH_SIZE} keys")
        pages = math.ceil(l/BATCH_SIZE)
        for p in range(0, pages):
          batch_keys = all_keys[p * BATCH_SIZE: p * BATCH_SIZE + BATCH_SIZE]
          batch_values = [map[i] for i in batch_keys]
          result = getTranslationsFor(batch_values, languageKey)
          if verbose:
            print("Translation Api Response Success")
          updateTranslationFile(result, batch_keys, languageKey)
          if verbose:
            print(f"'{languageKey}' translation file updated")
          updateLockFile(batch_keys, languageKey)
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
    print(e)
