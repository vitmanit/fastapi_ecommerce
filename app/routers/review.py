from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from sqlalchemy import select, insert
from app.schemas import CreateProduct
from app.models import *
from app.routers.auth import get_current_user


router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalar(select(Review).where(Review.is_active == True))
    all_reviews = reviews.all()

    if not all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = 'Reviews not found'
        )

    return all_reviews


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    reviews_product = db.scalars(select(Review).where(Review.product_id == product.id)).all()
    return reviews_product