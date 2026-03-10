import pytest
from fastapi import status
from icecream import ic
from sqlalchemy import select

from src.models.sellers import Seller
from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/sellers"


# Тест на ручку создающую продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Katy",
        "last_name": "Perry",
        "email": "kperry@gmail.com",
        "password": "DarkHorse1",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Katy",
        "last_name": "Perry",
        "email": "kperry@gmail.com"
    }


@pytest.mark.asyncio()
async def test_create_seller_with_wrong_password(async_client):
    data = {
        "first_name": "Katy",
        "last_name": "Perry",
        "email": "kperry@gmail.com",
        "password": "DarkH",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

@pytest.mark.asyncio()
async def test_create_seller_with_wrong_email(async_client):
    data = {
        "first_name": "Katy",
        "last_name": "Perry",
        "email": "kperry@gmail",
        "password": "DarkHorse1",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Lady", last_name="Gaga", email="l_gaga@hotmail.com", password="8pokerface")
    seller_2 = Seller(first_name="Miley", last_name="Cyrus", email="miley1992@mail.ru", password="flowers23")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Lady",
                "last_name": "Gaga",
                "email": "l_gaga@hotmail.com",
                "id": seller.id,
            },
            {
                "first_name": "Miley",
                "last_name": "Cyrus",
                "email": "miley1992@mail.ru",
                "id": seller_2.id,
            },
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client, auth_data):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку, которая
    # может случиться в POST ручке

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=auth_data["seller"]["id"])
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=198, seller_id=auth_data["seller"]["id"])

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{auth_data['seller']['id']}", headers=auth_data["headers"])

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Lady",
        "last_name": "Gaga",
        "email": "l_gaga@hotmail.com",
        "id": auth_data["seller"]["id"],
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "pages": 104,
                "id": book.id,
                "seller_id": auth_data["seller"]["id"]
            },

            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "pages": 198,
                "id": book_2.id,
                "seller_id": auth_data["seller"]["id"]
            },
        ]
    }


@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(async_client, auth_data):

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548", headers=auth_data["headers"])

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку обновления продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = Seller(first_name="Lady", last_name="Gaga", email="l_gaga@hotmail.com", password="8pokerface")

    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Robyn",
        "last_name": "Rihanna",
        "email": "customerservice@fentybeauty.com",
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller.id)
    assert res.first_name == "Robyn"
    assert res.last_name == "Rihanna"
    assert res.email == "customerservice@fentybeauty.com"
    assert res.id == seller.id


@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(first_name="Lady", last_name="Gaga", email="l_gaga@hotmail.com", password="8pokerface")

    db_session.add(seller)
    await db_session.flush()
    ic(seller.id)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=198, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_sellers = await db_session.execute(select(Seller))
    sellers_res = all_sellers.scalars().all()
    assert len(sellers_res) == 0

    all_books = await db_session.execute(select(Book))
    books_res = all_books.scalars().all()
    assert len(books_res) == 0



@pytest.mark.asyncio()
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    seller = Seller(first_name="Lady", last_name="Gaga", email="l_gaga@hotmail.com", password="8pokerface")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
