from src.schemas.pagination import PaginationParams, PagedResponse


class BaseService[T, ResponseSchema]:
    """
    Base service class
    """

    async def paginate(
        self,
        items: list[T] | list[ResponseSchema],
        total: int,
        pg_params: PaginationParams
    ) -> PagedResponse[ResponseSchema]:
        return PagedResponse.create(items, total, pg_params)
