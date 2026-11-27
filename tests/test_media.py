import pytest 

def test_get_seeded_book(client, seeded_db):
    expected = {"id": 1, **seeded_db[0]}

    response = client.get("/media/1")

    assert response.status_code == 200
    assert response.json() == expected

def test_list_books_empty(client):
    # No seed data

    response = client.get("/media/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_seeded_books(client, seeded_db):
    response = client.get("/media/", params={"limit": 100})

    assert response.status_code == 200
    assert len(response.json()) == len(seeded_db)


def test_create_book(client, sample_book):
    response = client.post("/media/", json=sample_book)

    assert response.status_code == 201
    data = response.json()

    assert isinstance(data["id"], int)

    for key, value in sample_book.items():
        assert data[key] == value


def test_create_book_is_saved(client, created_book):
    book_id = created_book["id"]

    response = client.get(f"/media/{book_id}")

    assert response.status_code == 200
    assert response.json() == created_book


def test_update_book(client, created_book, updated_book):
    book_id = created_book["id"]

    response = client.put(
        f"/media/{book_id}",
        json=updated_book
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == book_id

    for key, value in updated_book.items():
        assert data[key] == value

    get_response = client.get(f"/media/{book_id}")

    assert get_response.status_code == 200
    assert get_response.json() == data


def test_delete_book(client, created_book):
    book_id = created_book["id"]

    response = client.delete(f"/media/{book_id}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/media/{book_id}")

    assert get_response.status_code == 404

#---------------------------------------------------------------------------------
#UNHAPPY
#---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method, use_body",
    [
        ("get", False),
        ("put", True),
        ("delete", False),
    ],
    ids=["get", "put", "delete"],
)
def test_book_not_found(client, sample_book, method, use_body):
    kwargs = {"json": sample_book} if use_body else {}

    response = client.request(
        method,
        "/media/9999",
        **kwargs
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Media not found"}


def test_non_integer_id(client):
    response = client.get("/media/not-a-number")

    assert response.status_code == 422


def test_create_duplicate(client, created_book, sample_book):
    response = client.post("/media/", json=sample_book)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Media with that title and author/director already exists"
    }


def test_create_duplicate_ignores_case(
    client, created_book, sample_book
):
    duplicate_book = sample_book.copy()
    duplicate_book["title"] = duplicate_book["title"].upper()
    duplicate_book["author"] = duplicate_book["author"].lower()

    response = client.post("/media/", json=duplicate_book)

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Media with that title and author/director already exists"
    }


def test_update_into_duplicate(client, seeded_db):
    duplicate_book = seeded_db[0].copy()
    book_id = 2

    response = client.put(
        f"/media/{book_id}",
        json=duplicate_book
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Media with that title and author/director already exists"
    }

    get_response = client.get(f"/media/{book_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == seeded_db[1]["title"]


def test_update_same_title_and_author_is_allowed(
    client, created_book
):
    updated_data = created_book.copy()

    updated_data["description"] = "An updated book description."

    book_id = created_book["id"]

    response = client.put(
        f"/media/{book_id}",
        json=updated_data
    )

    assert response.status_code == 200
    assert response.json()["title"] == created_book["title"]
    assert response.json()["author"] == created_book["author"]
    assert response.json()["description"] == (
        "An updated book description."
    )

#===-----------------------------------------------------------------------
# Parametrizing values
#-------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "missing_field",
    [
        "title",
        "author",
        "release_year",
        "page_length",
        "description",
        "image_url",
    ],
    ids=[
        "title",
        "author",
        "release-year",
        "page-length",
        "description",
        "image-url",
    ],
)
def test_create_missing_field(client, sample_book, missing_field):
    book = sample_book.copy()
    book.pop(missing_field)

    response = client.post("/media/", json=book)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == [
        "body", missing_field
    ]


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("release_year", "nineteen-ninety-nine"),
        ("page_length", "two hundred"),
    ],
    ids=["year-not-int", "page-length-not-int"],
)
def test_create_invalid_value(client, sample_book, field, bad_value):
    book = sample_book.copy()
    book[field] = bad_value

    response = client.post("/media/", json=book)

    assert response.status_code == 422
