from src.models.user import User
from src.repos.project import ProjectRepository
from src.repos.task import TaskRepository
from src.schemas.project import ProjectResponse
from src.schemas.search import SearchResponse
from src.schemas.task import TaskResponse


class SearchService:
    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository
    ) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo

    async def search(self, query: str, limit: int, user: User) -> SearchResponse:
        tasks = await self.task_repo.search(query, user.id, limit)
        projects = await self.project_repo.search(query, user.id, limit)

        return SearchResponse(
            tasks=[TaskResponse.model_validate(task) for task in tasks],
            projects=[ProjectResponse.model_validate(project) for project in projects],
            total=len(tasks) + len(projects)
        )
