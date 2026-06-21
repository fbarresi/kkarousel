#!/usr/bin/env python3

import os
import uuid
import mimetypes
import urllib.request
import json


def upload_file(server_url, api_key, file_path):
    boundary = f"----PythonMultipart{uuid.uuid4().hex}"

    filename = os.path.basename(file_path)
    content_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = bytearray()

    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())
    body.extend(file_data)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url=server_url.rstrip("/") + "/upload",
        data=bytes(body),
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "X-API-Key": api_key,
        },
    )

    with urllib.request.urlopen(req) as response:
        result = response.read().decode("utf-8")
        try:
            return json.loads(result)
        except Exception:
            return result


if __name__ == "__main__":
    SERVER_URL = "https://whatever.com"
    API_KEY = "any key"
    FILE_PATH = "/tmp/image.jpg"

    response = upload_file(
        SERVER_URL,
        API_KEY,
        FILE_PATH,
    )

    print(response)
