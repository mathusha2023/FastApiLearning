from fastapi import APIRouter, UploadFile, HTTPException, Path
from typing import Annotated, Optional
import uuid
from sqlalchemy import select, delete
from src.api.dependencies import SessionDepend
from src.api.responsies import PNGResponse, response404
from src.models import CatModel, CatImageModel
from src.s3.s3_service import S3Service
from src.schemes import CatImageURLScheme, SuccessScheme
from src.settings import settings

router = APIRouter(tags=["Cats Images"], prefix="/cats_images")


@router.get("/{fp}",
            summary="Получить изображение котика",
            responses=response404("Изображение не найдено", "Изображение не найдено"),
            response_class=PNGResponse)
async def get_image(fp: str) -> PNGResponse:
    data = await S3Service.get_file_object(fp)
    if data is None:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    return PNGResponse(content=data)


@router.post("/{cat_id}",
             summary="Добавить картинку кота",
             responses=response404("Кот не найден", "Кот  с cat_id=1 не найден"))
async def post_image(cat_id: Annotated[int, Path(ge=1)], file: UploadFile, session: SessionDepend) -> CatImageURLScheme:
    if file.content_type != "image/png":
        raise HTTPException(status_code=422, detail="Некорректный формат файла: need png")

    query = select(CatModel).filter(CatModel.id == cat_id)
    res = await session.execute(query)
    cat: Optional[CatModel] = res.scalar()
    if cat is None:
        raise HTTPException(status_code=404, detail=f"Кот с {cat_id=} не найден!")

    filename = f"{uuid.uuid4()}.png"
    url = f"http://{settings.host}:{settings.port}/api/cats_images/{filename}"
    cat_image: CatImageModel = CatImageModel(cat_id=cat_id, image_url=url)
    session.add(cat_image)
    await session.commit()
    await S3Service.upload_file_object(content=file.file, object_name=filename)

    return CatImageURLScheme(image_url=url)


@router.delete("/{image_id}", summary="Удалить изображение")
async def delete_image(image_id: Annotated[int, Path(ge=1)], session: SessionDepend) -> SuccessScheme:
    query = delete(CatImageModel).filter(CatImageModel.id == image_id)
    await session.execute(query)
    await session.commit()
    return SuccessScheme()

