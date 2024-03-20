# 根据免费api提供的音乐点歌功能和热榜搜索功能

##  音乐插件
这个项目是[chatgpt-on-wechat](https://github.com/zhayujie/chatgpt-on-wechat) 的音乐插件, 实现以下功能：
- [x] 使用chatgpt 推荐音乐并发送音乐文件
- [x] 点歌/找歌并发送音乐文件

## 热榜功能
- [x] 发送包含知乎热榜,微博热搜,百度热点,历史上的今天,哔哩哔哩热搜,哔哩哔哩全站日榜,少数派头条,即可获取

### 使用方式

#### 命令安装
`#installp https://github.com/qiupo/apiMusic.git`
#### 插件集成
1. 把项目解压到chatgpt-on-wechat/plugins/apiMusic/ 目录下
2. 安装插件的依赖
```shell
cd /chatgpt-on-wechat/plugins/plugin_music/
pip3 install -r requirements.txt
```
3. 重新启动chatgpt-on-wechat
#### 触发

- 点歌: `点歌 可惜我是水瓶座`
- 推荐: `推荐一首欢快的歌曲`
- 热榜：`微博热榜`

ps: 借鉴[plugin_music](https://github.com/nautilis/plugin_music/tree/main)


