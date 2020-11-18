# GeekHub

GeekHub statusBar App Windows

[![Chat on Telegram](https://img.shields.io/badge/chat-Telegram-blueviolet?style=flat-square&logo=Telegram)](https://t.me/geekhub_app) [![Follow My Twitter](https://img.shields.io/badge/follow-Tweet-blue?style=flat-square&logo=Twitter)](https://twitter.com/LeetaoGoooo) [![Follow My Weibo](https://img.shields.io/badge/follow-Weibo-red?style=flat-square&logo=sina-weibo)](https://weibo.com/5984163100)

## 依赖

本程序依赖如下:

```
requests
beautifulSoup4
```
通过 `pip` 安装

```
pip install -r requirements.txt
```

## 运行

```
export debug=True
python geekhub/geekhub.py
```

## 打包
需要安装 `py2app`,通过 `pip install py2app` 安装
然后执行下面命令打包
```
python setup.py py2app
```
