from pydantic import BaseModel, ConfigDict, Field

#EVERYTHING FOR BOOK
class BookBase(BaseModel): 
    title        : str = Field(description = "Name of book") 
    author       : str = Field(description = "Name of who wrote the book")
    release_year : int = Field(description = "Year the book was released")
    page_length  : int = Field(description = "How many pages the book has")
    description  : str = Field(description = "A breif summary of the book")
    image_url    : str = Field(description = "URL to image related to book")


class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookRepsonse (BookBase):
    id: int  # include `id` in the response schema
    model_config = ConfigDict(from_attributes=True)    
