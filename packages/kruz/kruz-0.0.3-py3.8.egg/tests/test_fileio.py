import requests

def test_upload():
    url = 'https://api.bayfiles.com/upload'
    payload = open("request.json")
    r = requests.post(url, data=payload)