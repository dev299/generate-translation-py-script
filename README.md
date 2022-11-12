# Generate Translations

##Install Python Latest Version
## GO to the folder and run pip install -r requirements.txt
## Then run the following command
```
python main.py -t lang1,lang2 -v
```

```
{
    'method': 'POST',
    'url': `https://translation.googleapis.com/language/translate/v2?key=<CODE>&q=${message}&target=${language}`,
    'headers': {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
}
```
