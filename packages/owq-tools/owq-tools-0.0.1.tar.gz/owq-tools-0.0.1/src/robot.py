import base64
import hashlib
import hmac
import re
import time
import urllib.parse
from json import JSONDecodeError

import httpx
from loguru import logger


class DingtalkRobot:
    HEADERS = {'Content-Type': 'application/json; charset=utf-8'}

    def __init__(self, webhook: str, keywork: str = '', apikey: str = ''):
        """ Dingtalk group notifies the robot, supports text, link, and Markdown message notification.

        :param webhook: 钉钉群自定义机器人webhook地址
        :param keywork: 关键词, 发送消息时添加
        :param apikey: 安全配置->加密生成的KEY
        """

        self.webhook = webhook
        self.keywork = keywork
        self.secret = apikey

    def __str__(self) -> str:
        return f"Dingtalk Robot Info | webhook: {self.webhook}{self.keywork and f' | keywork: {self.keywork}'}"

    def _req_webhook(self, data: dict) -> bool:

        try:
            resp = httpx.post(self.webhook, headers=self.HEADERS, json=data, params=self.secret and self.get_sing())
            data = resp.json()
        except httpx.NetworkError as e:
            logger.error(f"Dingtalk robot send error: {e.args}")
        except JSONDecodeError:
            logger.error(f"Dingtalk robot send error: {resp.text}")
        else:
            _ = data.get('errcode') != 0 and logger.error(f"Dingtalk robot send error: {data.get('errmsg')}")
            return True

        return False

    def get_sing(self) -> dict:

        assert self.secret != None

        timestamp = int(time.time() * 1000)
        secret_enc = self.secret.encode('utf-8')
        sign_enc = f'{timestamp}\n{self.secret}'.encode('utf-8')
        hmac_code = hmac.new(secret_enc, sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return {
            'timestamp': timestamp,
            'sign': sign
        }

    def send_text(self, text: str, at_mobilese: list = [], at_user_ids: list = [], at_all: bool = False):

        if self.keywork:
            text = self.keywork + '\n\n' + text

        data = {
            "msgtype": "text",
            "text": {"content": text},
            "at": {
                "atMobiles": at_mobilese,
                "atUserIds": at_user_ids,
                "isAtAll": at_all
            }
        }
        return self._req_webhook(data)

    def send_link(self, link: str, text: str = '', title: str = '',  img_url: str = ''):

        if self.keywork:
            title = f"{self.keywork}\n\n{title}" if title else self.keywork

        data = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text or link,
                "picUrl": img_url,
                "messageUrl": link
            }
        }
        return self._req_webhook(data)

    def send_markdown(self, text: str = ..., file: str = ..., title: str = ..., at_mobilese: list = [], at_user_ids: list = [], at_all: bool = False):
        """ 发送 MarkDown 消息通知

        支持MD格式: 标题, 引用, 文字加粗/斜体, 链接, 图片, 列表
        """

        assert text or file

        if file:
            with open(file, 'r') as fd:
                text = fd.read()

        if not title and (match_title := re.search(r'# (.*?)\n', text)):
            title = match_title.group(1) if match_title else title
        if self.keywork:
            title = self.keywork+title if title else self.keywork

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobilese,
                "atUserIds": at_user_ids,
                "isAtAll": at_all
            }
        }
        return self._req_webhook(data)
