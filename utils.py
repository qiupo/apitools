import logging
import os
import tempfile
import requests
import re
from bridge.reply import Reply, ReplyType
from urllib.parse import urlparse
from plugins.event import EventContext


class Utils:
    def __init__(self, song_key: str, rb_key: str):
        self.song_key = song_key
        self.rb_key = rb_key

    rb_types = {
        # zhihu(知乎热榜) weibo(微博热搜) baidu(百度热点) history(历史上的今天) bilihot(哔哩哔哩热搜) biliall(哔哩哔哩全站日榜) sspai(少数派头条)
        "知乎热榜": "zhihu",
        "微博热搜": "weibo",
        "百度热点": "baidu",
        "历史上的今天": "history",
        "哔哩哔哩热搜": "bilihot",
        "哔哩哔哩全站日榜": "biliall",
        "少数派头条": "sspai",
    }

    def search_song(self, song_info):
        print(song_info)
        data = {"name": song_info, "y": 1, "n": 1, "apiKey": self.song_key}
        url = "https://api.linhun.vip/api/qqyy"
        resp = self.search(data, url)
        logging.error("search api, code:{}, resp:{}".format(resp["code"], resp))
        if resp["code"] is not None and resp["code"] == 200:
            url = ""
            name = ""
            ar = ""
            if resp["mp3"] is not None:
                url = resp["mp3"]
            if resp["name"] is not None:
                name = resp["name"]
            if resp["author"] is not None:
                ar = resp["author"]
            return url, name, ar
        else:
            logging.error("参数缺失, code:{}, resp:{}".format(resp["code"], resp))
            return "", "", ""

    def search_rb(self, type):
        print(type, self.rb_key)
        data = {"type": type, "apiKey": self.rb_key}
        url = "https://api.linhun.vip/api/jhrsrb"
        resp = self.search(data, url)
        logging.error("search api, code:{}, resp:{}".format(resp["code"], resp))
        data = []
        title = "暂无"
        subtitle = "暂无"
        update_time = "暂无"
        if resp["code"] is not None and resp["code"] == 200:
            if resp["data"] is not None:
                data = resp["data"]
            if resp["title"] is not None:
                title = resp["title"]
            if resp["subtitle"] is not None:
                subtitle = resp["subtitle"]
            if resp["update_time"] is not None:
                update_time = resp["update_time"]
        else:
            logging.error("参数缺失, code:{}, resp:{}".format(resp["code"], resp))
        return data, title, subtitle, update_time

    def _save_mp3_tempfile(self, url, e_context, song_name):
        # 使用requests获取音频内容
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:

            # 获取文件名和扩展名
            file_name, file_ext = os.path.splitext(urlparse(url).path)
            with tempfile.NamedTemporaryFile(
                prefix=song_name + ".", suffix=file_ext, delete=False
            ) as f:
                # 写入临时文件
                f.write(response.content)
                # 获取临时文件的路径
                temp_file_path = f.name

            print(file_name, file_ext)

            print(f"音频文件已保存到临时文件: {temp_file_path}")
            self._send_info(e_context, temp_file_path, ReplyType.VOICE)
            return
        else:
            print("无法下载音频文件")
            self._send_info(e_context, url, ReplyType.TEXT)
            return

    def _send_info(self, e_context: EventContext, content: str, type):
        reply = Reply(type, content)
        channel = e_context["channel"]
        channel.send(reply, e_context["context"])

    def request(self, url, data):
        # {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A300 Safari/602.1', 'Referer': 'https://music.163.com', 'Cookie': 'os=pc;appver=2.9.7'}
        session = requests.session()
        resp = session.post(url, data=data)

        print(resp.status_code)
        if resp.status_code != 200:
            return None, None, "http code {}".format(resp.status_code)

        return resp.json(), 200

    def search(self, data={}, url="https://api.linhun.vip/api/qqyy"):
        resp, code = self.request(url, data)
        logging.info("search resp json:{}-{}".format(resp, code))
        if code == 200:
            return resp
        else:
            logging.error("search buss code:{}, resp:{}".format(resp["code"], resp))
            return {code: ""}

    def is_valid_url(self, url):
        pattern = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return pattern.match(url) is not None

    def has_str(self, string: str, str: str):
        return string.find(str) is not -1
