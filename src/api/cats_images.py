from fastapi import APIRouter, UploadFile

from src.s3.s3_service import S3Service

router = APIRouter(tags=["Cats Images"], prefix="/cats_images")


@router.post("/{cat_id}")
async def post_image(cat_id, file: UploadFile):
    await S3Service.upload_file_object(object_name=file.filename, content=file.file)
    data = await S3Service.get_file_object("splash.png")
    print(data)
    # await S3Service.delete_file_object("splash.png")

    return {"Success": True}

