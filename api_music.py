import logging
import os
import tempfile
import requests
import plugins
from plugins import *
from common.log import logger
from bridge.bridge import Bridge
from bridge.context import ContextType
import re
from bridge.reply import Reply, ReplyType
from urllib.parse import urlparse


@plugins.register(
    name="Music",
    desire_priority=200,
    hidden=True,
    desc="基于网络接口搜索音乐的插件",
    version="0.1",
    author="qiupo",
)
class Music(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.apiKey = "b932144bab6bb6827457707e59455136"
        logger.info("[Music] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return
        query = e_context["context"].content
        logger.info("content => " + query)
        content = ""
        song_url = ""
        song_name = ""
        if query.startswith(f"点歌") or query.startswith(f"找歌"):
            msg = query.replace("点歌", "")
            msg = query.replace("找歌", "")
            msg = msg.strip()
            url, name, ar = self.search_song(msg)
            song_name = "{} - {}".format(name, ar)
            if self.is_valid_url(url):
                content = "为你找到：{} - {}".format(name, ar)
                song_url = url
            else:
                content = "找不到歌曲😮‍💨"
                logger.info("点歌 reply --> {}, url:{}".format(msg, url))
        elif query.startswith(f"推荐"):
            chat = Bridge().get_bot("chat")

            reply = chat.reply(query + " 以歌名 - 歌手的格式回复", e_context["context"])
            logger.info("music receive => query:{}, reply:{}".format(query, reply))

            url, name, ar = self.search_song(reply.content)
            song_name = "{} - {}".format(name, ar)
            if self.is_valid_url(url):
                content = "为你找到：{} - {} ".format(name, ar)
                song_url = url
            else:
                content = reply.content + "\n----------\n找不到相关歌曲😮‍💨"
                logger.info("点歌 reply --> {}, url:{}".format(reply.content, url))

        else:
            return
        self._send_info(e_context, content, ReplyType.TEXT)

        if self.is_valid_url(song_url):
            self._save_mp3_tempfile(song_url, e_context, song_name)
        e_context.action = EventAction.BREAK_PASS
        return

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

    def search(self, s: str):
        data = {"name": s, "y": 1, "n": 1, "apiKey": self.apiKey}
        url = "https://api.linhun.vip/api/qqyy"
        # +'?name='+s+'&y=1&n=1&apiKey='+self.apiKey
        resp, code = self.request(url, data)
        logger.info("search song resp json:{}-{}".format(resp, code))
        # logger.info("search song resp json:{},{}".format(response))
        if code == 200:
            if resp["code"] == 200:
                return resp
            else:
                logging.error(
                    "search song buss code:{}, resp:{}".format(resp["code"], resp)
                )
        else:
            logger.error("search song buss code:{}, resp:{}".format(resp["code"], resp))
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

    def get_help_text(self, verbose=False, **kwargs):
        help_text = "推荐音乐\n"
        help_text += " 推荐一首粤语经典歌曲"
        help_text += "点歌/找歌\n"
        help_text += " 找歌 可惜我是水瓶座 杨千嬅"
        return help_text

    def search_song(self, song_info):
        print(song_info)
        resp = self.search(song_info)
        if resp["code"] == 200:
            songid = resp["id"]
            name = resp["name"]
            ar = resp["author"]
            url = resp["mp3"]
            if songid is not None:
                return url, name, ar
            else:
                logger.error("song not found")
                return "", "", ""

        else:
            logger.error(
                "search buss code not 200, code:{}, resp:{}".format(resp["code"], resp)
            )
        return "", "", ""
