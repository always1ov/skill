---
name: upload-to-r2
description: 把本地图片/文件上传到 Cloudflare R2（cards 桶），返回可公网访问的 https://img.always1ov.com/<key> 链接。当需要把生成的卡片图、下载的境外图片等发到钉钉/飞书等国内客户端前，先用本技能本地化为可访问 URL 时使用。
---

# upload-to-r2

把一个本地文件上传到 R2 的 `cards` 桶，返回公网 URL。钉钉无法加载境外图床，
任何要推送的图片都应先经本技能上传，用返回的 https://img.always1ov.com/ 链接引用。

## 前置：环境变量（在智能体「环境变量」标签配置）
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY
- R2_ENDPOINT          (= https://fe20d8f6403b9675c2d944a866ca5da2.r2.cloudflarestorage.com)
- R2_PUBLIC_BASE       (= https://img.always1ov.com)

## 依赖
pip install boto3 --break-system-packages

## 用法
python upload.py <本地文件路径> [可选:目标key]
不传 key 时按日期+随机串自动命名。成功后 stdout 输出最终公网 URL。

## 给上层智能体的调用约定
1. 先确保图片已存为本地文件。
2. 运行 `python upload.py <文件路径>`，捕获 stdout 最后一行作为公网 URL。
3. 推钉钉时用 markdown：`![](<该URL>)`，text 中带上机器人安全关键词。
4. 失败排查：403/SignatureDoesNotMatch=密钥错；NoSuchBucket=桶名/endpoint 错；
   URL 打不开但上传成功=自定义域 img.always1ov.com 尚未变为"活动"状态，稍等。
