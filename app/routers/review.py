from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from app.backend.db_depends import get_db
from sqlalchemy import select, insert
from app.schemas import CreateProduct, CreateReview
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

@router.post('/{product_slug}/reviews')
async def add_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, create_review: CreateReview, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        product = db.scalar(select(Product).where(Product.slug == product_slug))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Product not found'
            )
        await db.execute(insert(Review).values(user_id=get_user.get('id'),
                                               product_id=product.id,
                                               comment=create_review.comment,
                                               grade=create_review.grade))

        all_reviews = db.scalars(select(Review.grade).where(Review.product_id == product.id)).all()
        if all_reviews:
            new_rating = sum(all_reviews) / len(all_reviews)
            product.rating = round(new_rating, 1)

        await db.commit()

        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )


@router.delete('/{review_id}')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    review_delete = db.scalar(select(Review).where(Review.id == review_id))

    if review_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
             )

    if get_user.get('is_admin') or review_delete.user_id == get_user.get('id'):
        if review_delete.is_active:
            review_delete.is_active = False
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Review delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Review is already deactivated'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
