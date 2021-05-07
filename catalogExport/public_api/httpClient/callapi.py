import requests


class CallApi:
    '''Class that allow to call multiple requests types'''
    def get(self, url, headers={}):
        print(url)
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res
        else:
            raise requests.models.HTTPError(
                f"HTTP {res.status_code}, aborting.\nBody: {res.text}")

    def patch(self, url, data, headers={}):
        res = requests.patch(url, headers=headers, json=data)
        # res = res.json()
        return res

    def post(self, url, data, headers={}):
        res = requests.post(url, headers=headers, json=data)
        # res = res.json()
        return res
