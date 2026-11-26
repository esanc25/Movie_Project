from sqlalchemy import Column, Integer, String

from app.database import Base


class Books(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column (String)
    release_year = Column(Integer)
    page_length = Column (Integer)
    description = Column(String)
    image_url = Column(String)
