---
name: upload-to-r2
description: 上传本地图片到 Cloudflare R2 并返回公网 URL，用于把图片本地化后推送到钉钉等国内客户端。
---

# upload-to-r2

把一个本地文件上传到 R2 的 cards 桶，返回公网 URL。钉钉无法加载境外图床，任何要推送的图片都应先经本技能上传，用返回的链接引用。

## 前置：环境变量（在智能体「环境变量」标签配置）

- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY
- R2_ENDPOINT
- R2_PUBLIC_BASE

## 依赖

pip install boto3 --break-system-packages

## 用法

python upload.py 本地文件路径 可选目标key

不传 key 时按日期加随机串自动命名。成功后 stdout 输出最终公网 URL。

## 给上层智能体的调用约定

1. 先确保图片已存为本地文件。
2. 运行 python upload.py 文件路径，捕获 stdout 最后一行作为公网 URL。
3. 推钉钉时用 markdown 图片语法引用该 URL，文本中带上机器人安全关键词。
4. 失败排查：403 或 SignatureDoesNotMatch 表示密钥错；NoSuchBucket 表示桶名或 endpoint 错；上传成功但 URL 打不开表示自定义域尚未生效，稍等。
