##  音乐插件
这个项目是[chatgpt-on-wechat](https://github.com/zhayujie/chatgpt-on-wechat) 的音乐插件, 实现以下功能：
- [x] 使用chatgpt 推荐音乐并发送音乐文件
- [x] 点歌/找歌并发送音乐文件

### 使用方式
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

ps: 借鉴[plugin_music](https://github.com/nautilis/plugin_music/tree/main)


