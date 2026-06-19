import os, sys, uuid, datetime, mimetypes
import boto3
from botocore.config import Config

BUCKET = "cards"

def main():
    if len(sys.argv) < 2:
        print("usage: python upload.py <file> [key]", file=sys.stderr); sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"file not found: {path}", file=sys.stderr); sys.exit(1)

    ext = os.path.splitext(path)[1] or ".bin"
    key = sys.argv[2] if len(sys.argv) > 2 else \
        f"{datetime.date.today():%Y/%m/%d}/{uuid.uuid4().hex}{ext}"

    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"

    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["R2_ENDPOINT"],
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    with open(path, "rb") as f:
        s3.put_object(Bucket=BUCKET, Key=key, Body=f, ContentType=ctype)

    base = os.environ["R2_PUBLIC_BASE"].rstrip("/")
    print(f"{base}/{key}")

if __name__ == "__main__":
    main()
