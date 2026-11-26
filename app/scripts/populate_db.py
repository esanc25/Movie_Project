from sqlalchemy.orm import Session

from app.database import engine
from app.models import Base, Books

book_data = [
    {
        "title" : "The Hunger Games",
        "author" : "Suzanne Collins",
        "release_year": 2008, 
        "page_length": 374,
        "description" : "In the future country of Panem, one girl anf one boy of each district must participate in the Hunger Games to fight to the death. In the 74th annual Hunger Games, Katniss Everdeen enters the arena to protect her little sister.",
        "image_url": "https://th.bing.com/th/id/R.42f9011d7898a452eb89c9cd7f1be7e3?rik=xJxwy2mLmEdFZQ&pid=ImgRaw&r=0"
    }, 

    {
        "title" : "Catching Fire",
        "author" : "Suzanne Collins",
        "release_year": 2009, 
        "page_length": 391,
        "description" : "After winning the 74th Hunger Games with her district partner, Peeta Mellark, Katniss Everdeen has to difuse the rebellious enviornment she created when she humiliated the Capitol in her Games, or else she risks the lives of everyone she loves.",
        "image_url": "https://embed.cdn.pais.scholastic.com/v1/channels/tso/products/identifiers/isbn/9780545586177/primary/renditions/700"
    }, 

    {
        "title" : "Mockingjay",
        "author" : "Suzanne Collins",
        "release_year": 2010, 
        "page_length": 390,
        "description" : "After escaping the arena, Katniss Everdeen agrees to become the Mockingjay, a symbol of the rebellion, to unify the districts of Panem in overthroughing the tyrannical Capitol.",
        "image_url": "https://th.bing.com/th/id/R.37d4e4b06adcc68fa238adacf6532ada?rik=z4v8iJPovkC9Og&pid=ImgRaw&r=0"
    }, 

]


def populate():
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        if session.query(Books).count() > 0 :
            return 
        for book in book_data:
            session.add(Books(**book))
        session.commit()

def reset():
    """Wipe the table and re-seed it. Run with `python -m app.scripts.populate_db`"""
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        session.query(Books).delete()
        session.commit()
    populate()



if __name__ == "__main__":
    populate()