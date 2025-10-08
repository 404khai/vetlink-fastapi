from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    posts = relationship("Posts", back_populates="owner")
    comments = relationship("Comments", back_populates="owner")


class PetOwner(Base):
    __tablename__ = "petOwners"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    userId = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="post")  # ✅ matches “post” in Comments


class Vet(Base):
    __tablename__ = "vets"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    dateCreated = Column(DateTime, default=datetime.utcnow, nullable=False)
    userId = Column(Integer, ForeignKey("users.id"))

    owner = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comments")