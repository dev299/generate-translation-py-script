import json
from typing import Dict

ENCODING = "utf-8-sig"


def readFile(file) -> Dict:
  try:
    with open(file, mode="r", encoding=ENCODING) as file:
      data = json.load(file)
  except FileNotFoundError as fileError:
    print(f"File '{file}' does not exist")
    raise fileError
  except json.decoder.JSONDecodeError as decodeError:
    print(f"File content of '{file}' not in json format, fix it manually")
    raise decodeError

  return data


def writeFile(file, data: Dict, **kwargs) -> None:
  try:
    with open(file, mode="w", encoding=ENCODING) as file:
      json.dump(data, file, **kwargs)
  except Exception as fileError:
    print(f"Failed to write content in file '{file}'")
    raise fileError
