# -*- coding: utf-8 -*-

import sys
import urllib
import time
import json
import pyconn.wx.config as cfg


class Token(object):
    def __init__(self, corp_id, corp_secret):
        self.baseurl = cfg.TOKEN_URL.format(corp_id, corp_secret)
        self.expire_time = sys.maxsize

    def get_token(self):
        if self.expire_time > time.time():
            request = urllib.request.Request(self.baseurl)
            response = urllib.request.urlopen(request)
            ret = response.read().decode('utf8').strip()
            ret = json.loads(ret)
            if 'errcode' in ret.keys():
                if ret['errcode'] != 0 or ret['errmsg'] != 'ok':
                    print('Get Wechat token Error: {}'.format(ret['errmsg']))
                    sys.exit(1)
            self.expire_time = time.time() + ret['expires_in']
            return ret['access_token']


class Wechat(object):
    def __init__(self, wechat_token):
        self.__token__ = wechat_token

    def send(self, msg):
        url = cfg.SEND_MSG_URL.format(self.__token__)
        payload = {
            "touser": "{0}".format(msg.receivers),
            "msgtype": "text",
            "agentid": msg.agentid,
            "text": {
                "content": "{0}".format(msg.content)

            },
            "safe": "0"
        }
        request = urllib.request.Request(url)
        request.add_header('Content-Type', 'application/json')
        ret = {}
        try:
            response = urllib.request.urlopen(request,
                                              json.dumps(payload, ensure_ascii=False).encode('utf-8')).read().decode(
                'utf-8')
            ret = json.JSONDecoder().decode(response)
        except urllib.error.URLError as e:
            print('Send Wechat Msg URLError:{}'.format(e.reason))
        return ret

    def send_file(self, receivers, filepath):
        import requests
        media_url = cfg.SEND_MEDIA_URL.format(self.__token__) + '&type=file'
        file = {'file': open(filepath, 'rb')}
        response = requests.post(media_url, files=file)
        media_id = json.loads(response.text)['media_id']
        payload = {
            "touser": receivers,
            "msgtype": "file",
            "agentid": "7",
            "file": {
                "media_id": media_id
            }
        }
        message_url = cfg.SEND_MSG_URL.format(self.__token__)
        response = requests.post(message_url, json.dumps(payload), headers={'Content-type': 'application/json'})
        return json.loads(response.text)


class WechatMessage:
    def __init__(self, agentid, receivers, content):
        timestamp = time.strftime('%m-%d %H:%M:%S', time.localtime(time.time()))
        self.agentid = agentid
        self.content = '%s\n[%s]' % (content, timestamp)
        self.receivers = receivers
