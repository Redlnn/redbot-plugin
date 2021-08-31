# redbot-plugin
一个用于放置 [redbot](https://github.com/Redlnn/redbot) 插件的仓库

__提醒：请不要直接将本项目的任意代码/代码片段直接copy走，copy请在注释里写上作者与项目地址__

## 用法
1. 进入 [redbot](https://github.com/Redlnn/redbot) 项目根目录，删除旧的 `plugins` 文件夹（请注意原有备份数据）
2. `git clone git@github.com:Redlnn/redbot-plugin.git plugins`
3. 进入 `plugins` 文件夹，使用 `pip install -r requirements.txt` 安装依赖
4. 返回 `redbot` 文件夹并启动 `redbot`

## 插件列表
格式：插件名 - 触发方式（若使用感叹号作为前缀则同时支持中英文感叹号）
1. [指令菜单](./Menu.py) - `!menu` | `!help`，需要 `文本转图片` 作为前置
2. [随机整数](./RollNumber.py) - `!roll` | `!roll {任意文本}`
3. [查询B站视频信息](./GetBilibiliVideoInfo.py)
```
 - 新版B站app分享的小程序
 - 旧版B站app分享的xml消息
 - B站概念版分享的json消息
 - 文字消息里含有B站视频地址，如 https://www.bilibili.com/video/av2
 - 文字消息里含有B站视频地址，如 https://www.bilibili.com/video/BV1xx411c7mD
 - 文字消息里含有B站视频地址，如 https://b23.tv/3V31Ap
 - !BV1xx411c7mD
 - !av2
```
4. [我的世界中文Wiki搜索](./SearchMinecraftWiki.py) - `!wiki {关键词}`
5. [文本转图片](./Text2Img/) - `!img {文本(支持换行)}`
6. [自动回复-精确匹配](./AutoReply/) - 需要 `文本转图片` 作为前置
7. [获取我的世界服务器信息](./MinecraftServerPing) - `!ping` | `!ping mc.hypixel.net:25565` | `!ping 127.0.0.1`
8. [人品检测](./RenpinChecker/) - `.jrrp` | `!jrrp` | `#jrrp` | `.jrrp`
9. [我的世界服务器管理](./MinecraftServerManger) - 建议直接看代码
10. ...
