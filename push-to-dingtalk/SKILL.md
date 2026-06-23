---
name: push-to-dingtalk
description: 通过 webhook 把文本、markdown 或图片消息推送到钉钉自定义机器人，超长内容自动分多条发完，图片需先有公网 URL。
---

# push-to-dingtalk

把消息推送到钉钉群的自定义机器人（webhook）。支持文本、markdown、图片三种。
单条超过钉钉长度上限时，自动按段拆成多条顺序发送，直到发完。
钉钉自定义机器人无法发本地图片文件，图片只能用公网 URL 引用，推图前应先用 upload-to-r2 把图传到 R2 拿到链接。

## 前置：环境变量（在智能体「环境变量」标签配置）

- DINGTALK_WEBHOOK　钉钉机器人 webhook 完整地址，含 access_token
- DINGTALK_SECRET　 可选，加签模式的 secret（以 SEC 开头）；不用加签留空
- DINGTALK_KEYWORD　可选，自定义关键词；机器人若用关键词安全设置，脚本会自动给消息带上

安全设置三选一：用关键词就配 DINGTALK_KEYWORD，用加签就配 DINGTALK_SECRET。

## 用法

```bash
python dingtalk.py text 内容
python dingtalk.py markdown 标题 markdown正文
python dingtalk.py image 公网图片URL 可选说明文字
```

成功后 stdout 输出钉钉返回的 JSON，errcode 为 0 表示成功。
内容超长会自动分多条发送，每条带（序号/总数）标记，条间留间隔避免频控。

## 调用约定

1. 纯文字通知用 text；富文本（链接、加粗、标题）用 markdown
2. 推图片：先用 upload-to-r2 上传得到公网链接，再用 image 模式推送
3. 不必担心长度，脚本自动分片；内容尽量多用换行，分片优先在换行处断开
4. 推送失败（errcode 非 0）直接报错退出，不重试，不自行实现推送逻辑

## 禁止

- 不得绕过此脚本自行构造 webhook 请求
- 不得在 agent prompt 里手动处理分片，脚本已处理
