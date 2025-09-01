from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from sqlalchemy import select, insert, update
from app.schemas import CreateProduct, CreateReview
from app.models import *
from app.routers.auth import get_current_user
from datetime import datetime


router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    reviews_list = reviews.all()
    if not reviews_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No active reviews'
        )

    return reviews_list


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    reviews = await db.scalars(select(Review).where(Review.product_id == product.id, Review.is_active == True))
    reviews_list = reviews.all()
    if not reviews_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active reviews found for this product")

    return reviews_list

@router.post('/{product_slug}/reviews')
async def create_review(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, create_review: CreateReview, get_user: Annotated[dict, Depends(get_current_user)]):
    if not get_user.get('is_customer'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )

    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found')

    await db.execute(insert(Review).values(
        user_id=get_user.get('id'),
        product_id=product.id,
        comment=create_review.comment,
        grade=create_review.rate
    ))

    reviews = await db.scalars(select(Review.grade).where(Review.product_id == product.id, Review.is_active == True))
    grades = reviews.all()
    if grades:
        new_rating = sum(grades) / len(grades)
        await db.execute(update(Product).where(Product.id == product.id).values(rating=round(new_rating, 1)))
    else:
        await db.execute(update(Product).where(Product.id == product.id).values(rating=0))

    await db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.delete('/{review_id}')
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)], review_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    review = await db.scalar(select(Review).where(Review.id == review_id, Review.is_active == True))
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found")

    if get_user.get('is_admin') or review.user_id == get_user.get('id'):
        await db.execute(update(Review).where(Review.id == review_id).values(is_active=False))
        await db.commit()
        return None
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have not enough permission for this action"
        )