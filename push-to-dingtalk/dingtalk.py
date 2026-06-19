import os, sys, time, hmac, hashlib, base64, urllib.parse, json
import urllib.request

# 环境变量:
#   DINGTALK_WEBHOOK   钉钉自定义机器人 webhook 完整地址(含 access_token)
#   DINGTALK_SECRET    可选,加签模式的 secret(以 SEC 开头);不用加签则留空
#   DINGTALK_KEYWORD   可选,自定义关键词;若机器人用关键词安全设置,文本里会自动带上

# 钉钉实测会"静默截断"超长消息(不报错、只丢后半段),且截断点远低于官方所说的 20000。
# 故阈值取保守值,宁可多分几条也不丢内容。可按实测结果用环境变量 DINGTALK_MAX_BYTES 覆盖。
MAX_BYTES = int(os.environ.get("DINGTALK_MAX_BYTES", "3500"))
# 同一批分片之间的间隔,避免触发频控(每分钟 20 条)
SLEEP_BETWEEN = 3.5

def signed_url(url, secret):
    ts = str(round(time.time() * 1000))
    string_to_sign = f"{ts}\n{secret}"
    h = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256)
    sign = urllib.parse.quote_plus(base64.b64encode(h.digest()))
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}timestamp={ts}&sign={sign}"

def _post_once(payload):
    url = os.environ["DINGTALK_WEBHOOK"]
    secret = os.environ.get("DINGTALK_SECRET", "").strip()
    if secret:
        url = signed_url(url, secret)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode("utf-8")
    print(body)
    res = json.loads(body)
    if res.get("errcode") != 0:
        sys.exit(f"dingtalk error: {body}")

def with_keyword(text):
    kw = os.environ.get("DINGTALK_KEYWORD", "").strip()
    if kw and kw not in text:
        return f"{kw} {text}"
    return text

def _split_by_bytes(text, limit):
    """按字节上限把文本切片,尽量在换行处断开,不切断多字节字符。"""
    chunks = []
    buf = ""
    buf_bytes = 0
    for line in text.splitlines(keepends=True):
        lb = len(line.encode("utf-8"))
        if lb > limit:
            # 单行超长,按字符硬切
            if buf:
                chunks.append(buf); buf = ""; buf_bytes = 0
            cur = ""
            cur_b = 0
            for ch in line:
                cb = len(ch.encode("utf-8"))
                if cur_b + cb > limit:
                    chunks.append(cur); cur = ""; cur_b = 0
                cur += ch; cur_b += cb
            if cur:
                buf = cur; buf_bytes = cur_b
            continue
        if buf_bytes + lb > limit:
            chunks.append(buf); buf = line; buf_bytes = lb
        else:
            buf += line; buf_bytes += lb
    if buf:
        chunks.append(buf)
    return chunks or [""]

def _send_chunks(make_payload, content, reserve):
    """把 content 分片后逐条发送。make_payload(piece, idx, total)->dict"""
    limit = MAX_BYTES - reserve
    pieces = _split_by_bytes(content, limit)
    total = len(pieces)
    for i, piece in enumerate(pieces, 1):
        _post_once(make_payload(piece, i, total))
        if i < total:
            time.sleep(SLEEP_BETWEEN)

def send_text(text):
    text = with_keyword(text)
    def mk(piece, i, total):
        body = piece if total == 1 else f"({i}/{total})\n{piece}"
        return {"msgtype": "text", "text": {"content": body}}
    # reserve 给 (i/total) 标记和关键词留余量
    _send_chunks(mk, text, reserve=80)

def send_markdown(title, text):
    title = with_keyword(title)
    text = with_keyword(text)
    def mk(piece, i, total):
        t = title if total == 1 else f"{title} ({i}/{total})"
        return {"msgtype": "markdown", "markdown": {"title": t, "text": piece}}
    _send_chunks(mk, text, reserve=80)

def send_image(image_url, caption=""):
    body = f"{caption}\n\n![]({image_url})" if caption else f"![]({image_url})"
    # 图片消息一般不会超限,直接走 markdown(含分片保护)
    send_markdown(caption or "图片", body)

def main():
    if len(sys.argv) < 2:
        print("usage:\n"
              "  python dingtalk.py text <内容>\n"
              "  python dingtalk.py markdown <标题> <markdown正文>\n"
              "  python dingtalk.py image <公网图片URL> [说明文字]\n"
              "超长内容会自动分多条发送,直到发完。",
              file=sys.stderr)
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "text":
        send_text(sys.argv[2])
    elif mode == "markdown":
        send_markdown(sys.argv[2], sys.argv[3])
    elif mode == "image":
        send_image(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        sys.exit(f"unknown mode: {mode}")

if __name__ == "__main__":
    main()
