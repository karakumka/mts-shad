__all__ = ["SellerService"]


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
        new_seller = Seller(
            **{
                "first_name": seller.first_name,
                "last_name": seller.last_name,
                "email": seller.email,
                "password": seller.password,
            }
        )

        self.session.add(new_seller)
        await self.session.flush()

        return new_seller

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)

        if seller:
            await self.session.delete(seller)
            return True

        else:
            return False

    async def update_seller(self, seller_id: int, new_seller_data: UpdateSeller) -> Seller | None:
        # book = fake_storage.get(book_id, None)
        # if book:
        # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
        if updated_seller := await self.session.get(Seller, seller_id):
            updated_seller.first_name = new_seller_data.first_name
            updated_seller.last_name = new_seller_data.last_name
            updated_seller.email = new_seller_data.email

            await self.session.flush()

            return updated_seller

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        seller = await self.session.get(Seller, seller_id)

        if seller is not None:
            await self.session.refresh(seller, ["books"])

        return seller

    async def get_all_sellers(self) -> list[Seller]:
        # Хотим видеть формат
        # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]

        query = select(Seller)  # SELECT * FROM boocs_table;
        result = await self.session.execute(query)  # await session.execute(select(Book))

        return result.scalars().all()
