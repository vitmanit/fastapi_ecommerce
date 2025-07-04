from _operator import and_

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert
from slugify import slugify
from sqlalchemy import select
from sqlalchemy import update

from app.backend.db_depends import get_db
from app.models import Category
from app.schemas import CreateProduct
from app.models.products import Product

router = APIRouter(prefix='/products', tags=['products'])


@router.get('/')
async def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(and_(Product.is_active, Product.stock > 0))).all()
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[Session, Depends(get_db)], create_product = CreateProduct):
    db.execute(insert(Product).values(name=create_product.name,
                                      slug=slugify(create_product.name),
                                      description=create_product.description,
                                      prict=create_product.price,
                                      image_url=create_product.image_url,
                                      stock=create_product.stock,
                                      category_id=create_product.category_id,
                                      rating=0.0))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)],  category_slug: str):
    category  = db.scalars(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Category not found'
        )
    lst_category = get_some_category_id(db, category.id)
    return db.scalars(select(Product).where(Product.category_id.in_(lst_category), Product.stock > 0)).all()

@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
    result = db.scalars(select(Product).where(Product.slug == product_slug))
    if result is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'There is no product found'
        )
    return result


@router.put('/{product_slug}')
async def update_product(product_slug: str):
    pass


@router.delete('/{product_slug}')
async def delete_product(product_slug: str):
    pass


def get_some_category_id(db: Session, category_id: int) -> list[int]:
    subcategories = db.scalars(select(Category).where(and_(Category.parent_id == category_id, Category.is_active))).all()

    if subcategories:
        lst = [category_id]
        for category in subcategories:
            lst+= get_some_category_id(db, category.id)
        return lst
    return [category_id]