import requests
import os
import json

FILE_NAME = "data.txt"

def upload():
    url = 'https://api.bayfiles.com/upload'
    f = open(FILE_NAME,"w"); f.write("test"); f.close()
    f = open(FILE_NAME,"r")
    files = {'file': (FILE_NAME, f)}
    r = requests.post('https://api.bayfiles.com/upload', files=files)
    print(r.content)
    data = json.loads(r.content)
    url = data["data"]["file"]["url"]["short"]
    id = url.replace("https://bayfiles.com/", "")
    print(id)
    assert r.status_code == 200
    f.close()
    os.remove(FILE_NAME)
    return id

def download(id):
    url = f'https://bayfiles.com/{id}/{FILE_NAME}'
    r = requests.get(url)
    print(r.content)
    assert r.status_code == 200

def test_code():
    id = upload()
    download(id)

test_code()
