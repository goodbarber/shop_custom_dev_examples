import requests


class CallApi:
    '''Class that allow to call multiple requests types'''
    def get(self, url, headers={}):
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res

    def patch(self, url, data, headers={}):
        res = requests.patch(url, headers=headers, json=data)
        res.raise_for_status()
        # res = res.json()
        return res

    def post(self, url, data, headers={}):
        res = requests.post(url, headers=headers, json=data)
        # res.raise_for_status()
        # res = res.json()
        return res

    def upload_file(self, url, data, headers={}):
        res = requests.post(url, headers=headers, files=data)
        res.raise_for_status()
        # res = res.json()
        return res

    def delete(self, url, headers={}):
        res = requests.delete(url, headers=headers)
        res.raise_for_status()
        return res
