# import requests
#
# url = "http://127.0.0.1:7777/DaenWxHook/httpapi/"
# data = {
#
#     "type": "Q0005",
#         "data": {},
#
#         }
# r = requests.post(url=url, json=data,)
# print(r.json())


import requests


# url = "http://127.0.0.1:7777/DaenWxHook/httpapi/?wxid=wxid_at1vbqt6zgg922"
# data = {"type": "Q0003",
#         "data": {},
#         }
# r = requests.post(url=url, json=data)
# print(r.json())


class Robot:
    """
    weixin python

    """

    def __init__(self):
        self.url = url
        self.wxid = wxid

    def command(self, name):
        url = self.url
        data = {"type": "Q0003",
                "data": {},
                }
        r = requests.post(url=url, json=data)
        print(r.json())

    def post_(self, type_, data_):
        url = self.url
        r = requests.post(url=url, json=data_, params={"wxid": f"{self.wxid}"})
        print(r.json())
        return r.json()

    def say(self, msg):
        type_ = "Q0001"
        data_ = {"type": f"{type_}",
                 "data": {"type": "1"},
                 }

        self.post_(type_, data_)

    def get_friend_list(self):
        type_ = "Q0005"
        data_ = {"type": f"{type_}",
                 "data": {"type": "1"},
                 }

        self.post_(type_, data_)



a=Robot("http://127.0.0.1:7777/DaenWxHook/httpapi/","wxid=wxid_at1vbqt6zgg922")
a.get_friend_list()