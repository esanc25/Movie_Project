from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Books
from app.schemas import BookCreate, BookRepsonse, BookUpdate

router = APIRouter (prefix='/media', tags = ["media"])
session = Depends(get_db)


NOT_FOUND_DETAIL = "Media not found"
CONFLICT_DETAIL  = "Media with that title and author/director already exists"

NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"description": NOT_FOUND_DETAIL}}
CONFLICT: dict[int | str, dict[str, Any]] = {409: {"description": CONFLICT_DETAIL}}
                                              

# 404 exception
def get_book_or_404(book_id: int, db: Session) -> Books:
    book = db.query(Books).filter(Books.id == book_id).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL
        )
    return book

# Checking duplicates 
def check_for_duplicate(
    title: str, author: str, db: Session, ignore_id: int | None = None
) -> None:
    """Raise a 409 if another book already has this title and author (ignoring case)."""
    query = db.query(Books).filter(
        func.lower(Books.title) == title.lower(),  
        func.lower(Books.author) == author.lower(), 
    )
    if ignore_id is not None:
        query = query.filter(Books.id != ignore_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=CONFLICT_DETAIL
        )


# Return list of Books 
@router.get("/", response_model=list[BookRepsonse])
def read_all(skip: int = 0, limit: int = 10, db: Session = session):
    books = db.query(Books).offset(skip).limit.all()
    return books


#Read one book 
@router.get("/{book_id}", response_model=BookRepsonse)
def read_one (book_id: int, db:Session = Depends(get_db)):
    books = db.query(Books).filter(Books.id == book_id).first()

    if books is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return books




#Update Book
@router.put(
    "/{book_id}", response_model=BookRepsonse, responses={**NOT_FOUND, **CONFLICT}
)
def update_book(
    book_id: int, book: BookUpdate, db: Session = Depends(get_db)
):
    """
    Replace every field of an existing book.

    Returns 404 if no book has that ID, and 409 if the new title and author
    match a *different* book.
    """
    db_book = get_book_or_404(book_id, db)
    check_for_duplicate(book.title, book.author, db, ignore_id=book_id)
    for field, value in book.model_dump().items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book

#Posting book 
@router.post(
    "/",
    response_model=BookRepsonse,                #endpoint uses this to ensure the data matches BookResponse schema
    status_code=status.HTTP_201_CREATED, 
    responses=CONFLICT,
)
def create_book(book: BookCreate, db: Session = Depends(get_db)): #BookCreate validated request body
    """
    Create a new book and return it with its new ID.

    Returns 409 if a book with the same title and author already exists
    (not case-sensitive).
    """
    check_for_duplicate(book.title, book.author, db)
    db_book = Books(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

#Delete Book
@router.delete(
    "/{book_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book. Returns 204 with no body, or 404 if no book has that ID."""
    db_book = get_book_or_404(book_id, db)
    db.delete(db_book) #CHNAGE BACK
    db.commit()
