from typing import Annotated
from fastapi import FastAPI, Depends, Header, Security, UploadFile, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import Response
import io
import PIL
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
filename = "cover.png"
env_var_api_key = "API-KEY"
width = 600
height = 800

# load api keys or generate it if not exists
try:
    from keys import api_keys
except (Exception) as e:
    print("no secrets found. Generating new api key.", e)
    import uuid
    import os
    key = ""
    if env_var_api_key in os.environ:
        key = os.environ[env_var_api_key]
    if key == "":
        key = str(uuid.uuid4())
    api_keys = [key]
    with open("keys.py", "w") as text_file:
        text_file.write("api_keys = ['{key}']".format(key=key))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(api_key_header: str = Security(api_key_header)):
    if api_key_header not in api_keys:
        raise HTTPException(status_code=401, detail="invalid api key")


app = FastAPI(
    dependencies=[
        Depends(verify_key),
    ]
)

@app.post("/upload")
async def upload_image(file: UploadFile):
    allowed = allowed_file(file.filename)
    if not allowed:
         raise HTTPException(status_code=403, detail="invalid file extension")
    content = await file.read()
    rawBytes = io.BytesIO(content)
    size = (width, height)
    image = Image.open(rawBytes).resize(size).convert('L')
    image.save(filename)
    return True

@app.get("/download", responses = {200: {"content": {"image/png": {}}}}, response_class=Response)
async def download_image():
    with open(filename, "rb") as file:
        return Response(content=file.read(), media_type="image/png")
