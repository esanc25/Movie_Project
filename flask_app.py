import requests
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for, flash


API_URL = "http://localhost:8000/media/"

app = Flask (__name__)


#HOmepage
@app.route("/")
def home():
    return render_template("index.html")



#------------------------
# Add A book
#------------------------
@app.route("/add_book", methods=["GET","POST"])
def add(): 
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        release_year = request.form.get("release_year", "").strip()
        page_length = request.form.get("page_length", "").strip()
        description = request.form.get("description", "").strip()
        image_url = request.form.get("image_url", "").strip()

        #each book needs a title and author
        if not title or not author:
            return render_template(
                "add.html", error = "Title and author are required"
            )

        #new book to databse
        new_book = {
            "title": title,
            "author": author,
            "release_year": release_year,
            "page_length": page_length,
            "description": description,
            "image_url": image_url
        }

        try:
            response = requests.post(
                API_URL,
                json=new_book,
                timeout=10
            )

            response.raise_for_status()

        except requests.exceptions.HTTPError:
            error_message = response.json().get(
                "detail", "Unable to add book"
            )

            return render_template(
                "add.html",
                error=error_message
            )

        except requests.exceptions.RequestException:
            return render_template(
                "add.html",
                error="Could not connect to the book API"
            )

        return redirect(
            url_for("confirmation", title=title)
        )

    return render_template("add.html")


@app.route("/confirmation")
def confirmation():
    title = request.args.get("title", "friend")

    response = requests.get(API_URL, params={"limit": 100}, timeout=10)
    response.raise_for_status()
    books = response.json()

    count = len(books)

    return render_template("confirmation.html", title=title, count=count)


#------------------------
# Search for A book
#------------------------
@app.route("/search_book", methods=["GET", "POST"])
def search_one():
    if request.method == "POST":
        book_id = request.form.get("id", "").strip()

        if not book_id.isdigit():
            return render_template(
                "search_one.html",
                error="Please enter a valid book ID."
            )
        
        try:
            response = requests.get(
                f"{API_URL}{book_id}",
                timeout=10
            )
            response.raise_for_status()
            book = response.json()

            return render_template("search_one.html", book=book)

        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                return render_template(
                    "search_one.html",
                    error="No book found with that ID."
                )

            return render_template(
                "search_one.html",
                error="Something went wrong while searching."
            )

        except requests.exceptions.RequestException:
            return render_template(
                "search_one.html",
                error="Could not connect to the API."
            )

    return render_template("search_one.html")



#------------------------
# Edit a book 
#------------------------
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        book_id = request.form.get("id", "").strip()

        if not book_id.isdigit():
            return render_template(
                "edit_lookup.html",
                error="Please enter a valid book ID."
            )

        return redirect(url_for("edit_book", book_id=book_id))

    return render_template("edit_lookup.html")


# Edit an existing book
@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    try:
        response = requests.get(
            f"{API_URL}{book_id}",
            timeout=10
        )
        response.raise_for_status()
        book = response.json()

    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            return render_template(
                "edit_lookup.html",
                error="No book found with that ID."
            )

        return render_template(
            "edit_lookup.html",
            error="Unable to retrieve the book."
        )

    except requests.exceptions.RequestException:
        return render_template(
            "edit_lookup.html",
            error="Could not connect to the book API."
        )

    # Update the book when the form is submitted
    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        release_year = request.form.get("release_year", "").strip()
        page_length = request.form.get("page_length", "").strip()
        description = request.form.get("description", "").strip()
        image_url = request.form.get("image_url", "").strip()

        if not title or not author:
            return render_template(
                "edit_book.html",
                book=book,
                error="Title and author are required."
            )

        try:
            updated_book = {
                "title": title,
                "author": author,
                "release_year": int(release_year),
                "page_length": int(page_length),
                "description": description,
                "image_url": image_url
            }

        except ValueError:
            return render_template(
                "edit_book.html",
                book=book,
                error="Release year and page length must be numbers."
            )

        try:
            response = requests.put(
                f"{API_URL}{book_id}",
                json=updated_book,
                timeout=10
            )
            response.raise_for_status()

            return redirect(
                url_for("edit_book", book_id=book_id, updated="true")
            )

        except requests.exceptions.HTTPError:
            error_message = response.json().get(
                "detail", "Unable to update book."
            )

            return render_template(
                "edit_book.html",
                book=book,
                error=error_message
            )

        except requests.exceptions.RequestException:
            return render_template(
                "edit_book.html",
                book=book,
                error="Could not connect to the book API."
            )

    return render_template(
        "edit_book.html",
        book=book,
        updated=request.args.get("updated")
    )

#----------------------
#Delete Book
#---------------------


@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        book_id = request.form.get("id", "").strip()

        if not book_id.isdigit():
            return render_template(
                "delete_lookup.html",
                error="Please enter a valid BookID"
            )

        #book info before deleting
        book_response = requests.get(f"{API_URL}{book_id}")

        if book_response.status_code != 200:
            return render_template(
                "delete_lookup.html",
                error="Book not found."
            )

        book = book_response.json()
        book_title = book["title"]

        # Delete the book
        response = requests.delete(f"{API_URL}{book_id}")

        if response.status_code == 204:
            return render_template(
                "delete_lookup.html",
                error=f'"{book_title}" was deleted successfully!'
            )
        else:
            return render_template(
                "delete_lookup.html",
                message="Failed to delete book. Please try again."
            )

    return render_template("delete_lookup.html")


#-------------------------
#Show all covers 
#-----------------------

@app.route("/books")
def all_books():
    response = requests.get(API_URL)

    if response.status_code == 200:
        books = response.json()
        return render_template("books.html", books=books)

    return render_template(
        "books.html",
        books=[],
        error="Unable to retrieve books."
    )



if __name__ == "__main__":
    app.run(debug=True, port=5000)
    