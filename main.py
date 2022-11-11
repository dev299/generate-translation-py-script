import argparse
import math
from dotenv import load_dotenv
from api import getTranslationsFor
from typing import List, Dict
from fileutil import readFile, writeFile
load_dotenv()

BATCH_SIZE = 20


def loadDefaultI18n():
  return readFile("translations/en.json")


def getKeys(allKeys: List[str], languageKey: str):
  filename = ".lock/" + languageKey + ".mo"
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
  filename = ".lock/" + languageKey + ".mo"
  lockMap: Dict = readFile(filename)
  for key in successKeys:
    lockMap.update({key: 1})

  writeFile(filename, lockMap)


def updateTranslationFile(apiResponse, keys, languageKey, retried=False):
  filename = "translations/"+languageKey+".json"
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


def run(target: List[str] = None, verbose=False):
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
  run(target=str(args.target).split(sep=","), verbose=args.verbose)
