from fastapi import APIRouter, status

from app.api.deps import CurrentUser, Pagination, RoadmapSvc
from app.schemas.roadmap_schema import RoadmapCreate, RoadmapRead

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


@router.post("", response_model=RoadmapRead, status_code=status.HTTP_202_ACCEPTED)
async def request_roadmap(payload: RoadmapCreate, user: CurrentUser, service: RoadmapSvc):
    """Queues roadmap generation for a completed interview (idempotent per session)."""
    return await service.request_generation(user, payload.session_uuid)


@router.get("", response_model=list[RoadmapRead])
async def list_roadmaps(user: CurrentUser, service: RoadmapSvc, page: Pagination):
    return await service.list_for_user(user, page.skip, page.limit)


@router.get("/{roadmap_uuid}", response_model=RoadmapRead)
async def get_roadmap(roadmap_uuid: str, user: CurrentUser, service: RoadmapSvc):
    return await service.get_owned(user, roadmap_uuid)
