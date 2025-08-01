from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.backend.db import Base

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(String)
    comment_date = Column(DateTime, default=datetime.utcnow)  # или datetime.now()
    grade = Column(Integer)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")