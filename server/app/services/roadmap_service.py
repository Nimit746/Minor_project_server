import logging

from pymongo.asynchronous.database import AsyncDatabase

from app.core.exceptions import ConflictException, NotFoundException, ServiceUnavailableException
from app.db.base_repository import BaseRepository
from app.models.interview_model import InterviewSessionModel
from app.models.roadmap_model import RoadmapModel
from app.models.user_model import UserModel

logger = logging.getLogger(__name__)


class RoadmapService:
    def __init__(self, db: AsyncDatabase, arq_pool):
        self.roadmaps = BaseRepository(db["roadmaps"], RoadmapModel)
        self.sessions = BaseRepository(db["interview_sessions"], InterviewSessionModel)
        self.arq = arq_pool

    async def request_generation(self, user: UserModel, session_uuid: str) -> RoadmapModel:
        session = await self.sessions.get_one({"uuid": session_uuid, "user_uuid": user.uuid})
        if session is None:
            raise NotFoundException("Interview session")
        if session.status != "completed":
            raise ConflictException("Roadmap can only be generated for a completed interview")

        existing = await self.roadmaps.get_one({"session_uuid": session_uuid})
        if existing is not None and existing.status != "failed":
            return existing  # idempotent: pending / processing / ready
        if existing is not None:  # retry a failed one
            roadmap = await self.roadmaps.update_by_uuid(
                existing.uuid, {"status": "pending", "error": None}
            )
        else:
            roadmap = await self.roadmaps.create(
                RoadmapModel(user_uuid=user.uuid, session_uuid=session_uuid)
            )

        try:
            # unique job id => double-clicks don't queue duplicate (expensive) LLM jobs
            await self.arq.enqueue_job(
                "generate_roadmap", roadmap.uuid, _job_id=f"roadmap:{roadmap.uuid}:{roadmap.updated_at.timestamp()}"
            )
        except Exception:
            logger.exception("Failed to enqueue roadmap %s", roadmap.uuid)
            await self.roadmaps.update_by_uuid(
                roadmap.uuid, {"status": "failed", "error": "Could not queue generation job"}
            )
            raise ServiceUnavailableException("Processing queue unavailable, please retry")
        return roadmap

    async def get_owned(self, user: UserModel, roadmap_uuid: str) -> RoadmapModel:
        roadmap = await self.roadmaps.get_one({"uuid": roadmap_uuid, "user_uuid": user.uuid})
        if roadmap is None:
            raise NotFoundException("Roadmap")
        return roadmap

    async def list_for_user(self, user: UserModel, skip: int, limit: int) -> list[RoadmapModel]:
        return await self.roadmaps.find_many({"user_uuid": user.uuid}, skip=skip, limit=limit)
