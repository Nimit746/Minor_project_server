import asyncio
import logging
from pathlib import Path

from fastapi import UploadFile
from pymongo.asynchronous.database import AsyncDatabase

from app.config.settings import get_settings
from app.core.exceptions import (
    AppException,
    BadRequestException,
    NotFoundException,
    ServiceUnavailableException,
)
from app.db.base_repository import BaseRepository
from app.models.resume_model import ResumeModel
from app.models.user_model import UserModel

logger = logging.getLogger(__name__)

ALLOWED = {
    ".pdf": ("application/pdf", b"%PDF"),
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        b"PK\x03\x04",  # docx is a zip container
    ),
}


def _write_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class ResumeService:
    def __init__(self, db: AsyncDatabase, arq_pool):
        self.repo = BaseRepository(db["resumes"], ResumeModel)
        self.arq = arq_pool

    async def create_from_upload(self, user: UserModel, file: UploadFile) -> ResumeModel:
        s = get_settings()
        original_name = Path(file.filename or "resume").name  # strip any client-supplied path
        ext = Path(original_name).suffix.lower()
        if ext not in ALLOWED:
            raise BadRequestException("Only .pdf and .docx resumes are supported")

        content = await file.read(s.max_resume_bytes + 1)
        if not content:
            raise BadRequestException("Uploaded file is empty")
        if len(content) > s.max_resume_bytes:
            raise AppException(f"File exceeds {s.MAX_RESUME_MB} MB limit", 413)
        content_type, magic = ALLOWED[ext]
        if not content.startswith(magic):  # don't trust the extension alone
            raise BadRequestException("File content does not match its extension")

        resume = ResumeModel(
            user_uuid=user.uuid,
            filename=original_name[:200],
            content_type=content_type,
            size_bytes=len(content),
            file_path="",
        )
        # stored name is our uuid, never the client's filename
        path = Path(s.UPLOAD_DIR) / user.uuid / f"{resume.uuid}{ext}"
        resume.file_path = str(path)
        await asyncio.to_thread(_write_file, path, content)
        await self.repo.create(resume)

        try:
            await self.arq.enqueue_job("ingest_resume", resume.uuid, _job_id=f"resume:{resume.uuid}")
        except Exception:
            logger.exception("Failed to enqueue resume %s", resume.uuid)
            await self.repo.update_by_uuid(
                resume.uuid, {"status": "failed", "error": "Could not queue processing job"}
            )
            raise ServiceUnavailableException("Processing queue unavailable, please retry")
        return resume

    async def get_owned(self, user: UserModel, resume_uuid: str) -> ResumeModel:
        resume = await self.repo.get_one({"uuid": resume_uuid, "user_uuid": user.uuid})
        if resume is None:
            raise NotFoundException("Resume")
        return resume

    async def list_for_user(self, user: UserModel, skip: int, limit: int) -> list[ResumeModel]:
        return await self.repo.find_many({"user_uuid": user.uuid}, skip=skip, limit=limit)

    async def delete(self, user: UserModel, resume_uuid: str) -> None:
        resume = await self.get_owned(user, resume_uuid)
        await self.repo.delete_by_uuid(resume.uuid)
        try:
            await asyncio.to_thread(Path(resume.file_path).unlink, True)
        except OSError:
            logger.warning("Could not delete file %s", resume.file_path)
