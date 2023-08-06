from requests import post
from hashlib  import sha256
from json     import loads, dumps


class Migurdia:
    apiUrl    = 'https://migurdia.yukiteru.xyz/API.php'
    sessionID = 0

    async def login(self, username, password):
        data = {
            'method'  : 'signin',
            'username': username,
            'password': sha256(password.encode('utf-8')).hexdigest()
        }

        response = post(self.apiUrl, data=data)

        if response.status_code             != 200: return None
        if loads(response.text)['exitCode'] !=   0: return None

        self.sessionID = loads(response.text)['result']['SID']

    async def addPost(self, fileUrl, thumbnailUrl, tags=[], title='Untitled', description=''):
        data = {
            'method': 'addPosts',
            'posts' : dumps([{
                'title'       : title,
                'description' : description,
                'tags'        : tags,
                'thumbnailUrl': thumbnailUrl,
                'fileUrl'     : fileUrl
            }])
        }

        response = post(self.apiUrl, data=data, headers={ 'Cookie': f"PHPSESSID={self.sessionID}" })

        if response.status_code             != 200: return None
        if loads(response.text)['exitCode'] !=   0: return None

        return loads(response.text)
