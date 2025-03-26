from typing import List, Annotated, Optional, Dict

from fastapi import APIRouter, Path, HTTPException
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.dependencies import SessionDepend
from src.api.responsies import response404
from src.models import CatModel
from src.schemes import CatScheme, CatFullScheme, CatAddScheme, CatPatchScheme, SuccessScheme

router = APIRouter(tags=["Cats"], prefix="/cats")


@router.get("",
            summary="Получить всех котов")
async def get_cats(session: SessionDepend) -> List[CatScheme]:
    query = select(CatModel).order_by(CatModel.id)
    res = await session.execute(query)
    cats = res.scalars().all()
    cats_schemes = [CatScheme.model_validate(cat) for cat in cats]
    return cats_schemes


@router.get("/{cat_id}",
            summary="Получить кота по id",
            responses=response404("Кот не найден", "Кот  с cat_id=1 не найден"))
async def get_cat(cat_id: Annotated[int, Path(ge=1)], session: SessionDepend) -> CatFullScheme:
    query = select(CatModel).options(selectinload(CatModel.images)).filter(CatModel.id == cat_id)
    res = await session.execute(query)
    db_cat: Optional[CatModel] = res.scalar()
    if db_cat is None:
        raise HTTPException(status_code=404, detail=f"Кот с {cat_id=} не найден!")
    return CatFullScheme.model_validate(db_cat)


@router.post("", summary="Добавить кота")
async def add_cat(cat: CatAddScheme, session: SessionDepend) -> SuccessScheme:
    db_cat = CatModel(name=cat.name, birthday=cat.birthday, color=cat.color)
    session.add(db_cat)
    await session.commit()
    return SuccessScheme()


@router.put("/{cat_id}",
            summary="Изменить все данные кота",
            responses=response404("Кот не найден", "Кот  с cat_id=1 не найден"))
async def put_cat(cat_id: Annotated[int, Path(ge=1)], cat: CatAddScheme, session: SessionDepend) -> CatFullScheme:
    query = select(CatModel).options(selectinload(CatModel.images)).filter(CatModel.id == cat_id)
    res = await session.execute(query)
    db_cat: Optional[CatModel] = res.scalar()
    if db_cat is None:
        raise HTTPException(status_code=404, detail=f"Кот с {cat_id=} не найден!")
    db_cat.birthday = cat.birthday
    db_cat.color = cat.color
    db_cat.name = cat.name
    await session.commit()
    return CatFullScheme.model_validate(db_cat)


@router.patch("/{cat_id}",
              summary="Изменить часть данных кота",
              responses=response404("Кот не найден", "Кот  с cat_id=1 не найден"))
async def patch_cat(cat_id: Annotated[int, Path(ge=1)], cat: CatPatchScheme, session: SessionDepend) -> CatFullScheme:
    query = select(CatModel).options(selectinload(CatModel.images)).filter(CatModel.id == cat_id)
    res = await session.execute(query)
    db_cat: Optional[CatModel] = res.scalar()
    if db_cat is None:
        raise HTTPException(status_code=404, detail=f"Кот с {cat_id=} не найден!")
    if cat.birthday:
        db_cat.birthday = cat.birthday
    if cat.color:
        db_cat.color = cat.color
    if cat.name:
        db_cat.name = cat.name
    await session.commit()
    return CatFullScheme.model_validate(db_cat)


@router.delete("/{cat_id}",
               summary="Удалить кота",
               responses=response404("Кот не найден", "Кот  с cat_id=1 не найден"))
async def delete_cat(cat_id: Annotated[int, Path(ge=1)], session: SessionDepend) -> CatFullScheme:
    query = select(CatModel).options(selectinload(CatModel.images)).filter(CatModel.id == cat_id)
    res = await session.execute(query)
    db_cat: Optional[CatModel] = res.scalar()
    if db_cat is None:
        raise HTTPException(status_code=404, detail=f"Кот с {cat_id=} не найден!")
    await session.delete(db_cat)
    await session.commit()
    return CatFullScheme.model_validate(db_cat)
