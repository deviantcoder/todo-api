from fastapi import APIRouter

from src.api.deps.auth import CurrentUserDep
from src.api.deps.search import SearchParamsDep, SearchServiceDep
from src.schemas.search import SearchResponse

router = APIRouter(prefix='/search', tags=['search'])


@router.get('/', response_model=SearchResponse)
async def search(
    service: SearchServiceDep,
    current_user: CurrentUserDep,
    params: SearchParamsDep
) -> SearchResponse:
    return await service.search(params.query, params.limit, current_user)
