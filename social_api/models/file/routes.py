from fastapi import APIRouter
from social_api import GC_BUCKET, GC_CLOUD_CLIENT
from starlette.requests import Request

# init new rouer:
router = APIRouter()


@router.post("/upload", tags=["file"])
async def upload(request: Request):
    from starlette.datastructures import UploadFile
    file = await request.form()
    file: UploadFile = file['file_0']

    blob = GC_BUCKET.blob(file.filename)

    blob.upload_from_string(
        await file.read(),
        content_type=file.content_type
    )
    await file.close()

    return blob.public_url
