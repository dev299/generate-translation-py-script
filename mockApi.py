# {
# 'data': {
#   'translations': [
#     {'translatedText': 'Salut je suis John', 'detectedSourceLanguage': 'en'},
#     {'translatedText': 'Salut comment ca va?', 'detectedSourceLanguage': 'en'}
#     ]
#   }
# }
def get_dummy_response(length: int):
  map = {"data": {
      "translations": []
  }}
  for _ in range(length):
    map.get("data").get("translations").append({
        "translatedText": '你好', "detectedSourceLanguage": "en"
    })

  return map
