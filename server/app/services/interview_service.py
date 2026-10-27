"""Interview orchestration: HTTP request  <->  LangGraph (interrupt/resume)  <->  Mongo.

Flow (thread_id == session uuid, state persisted by the graph's checkpointer):
  start  -> graph.ainvoke(initial_state)        -> runs until `interrupt_for_answer` -> 1st question
  answer -> graph.ainvoke(Command(resume=text)) -> evaluates, then next interrupt (or END)

!! ADAPTER SECTION (top of class) is the ONLY place that knows your graph's state keys.
   If your `session_state.py` uses different names, edit `_initial_state`, `_pending_interrupt`,
   `_normalize_question`, `_extract_evaluation` and `_extract_summary` - nothing else.
"""
import logging
from typing import Any

from langgraph.types import Command
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.config.settings import get_settings
from app.core.exceptions import AppException, ConflictException, NotFoundException
from app.db.base_repository import BaseRepository
from app.models.interview_model import InterviewSessionModel, Turn
from app.models.resume_model import ResumeModel
from app.models.user_model import UserModel
from app.schemas.interview_schema import InterviewCreate, InterviewTurnResponse, TurnRead
from app.utils.datetime_utils import _now

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(self, db: AsyncDatabase, graph):
        self.col = db["interview_sessions"]
        self.sessions = BaseRepository(self.col, InterviewSessionModel)
        self.resumes = BaseRepository(db["resumes"], ResumeModel)
        self.graph = graph

    # ------------------------------------------------------------------ ADAPTERS
    @staticmethod
    def _initial_state(user: UserModel, session: InterviewSessionModel, resume: ResumeModel) -> dict:
        diff_map = {"beginner": 1, "easy": 2, "medium": 3, "hard": 4, "expert": 5}
        difficulty_num = (
            diff_map.get(str(session.difficulty).lower(), 2)
            if isinstance(session.difficulty, str)
            else (session.difficulty or 2)
        )

        return {
            "candidate_id": user.uuid,
            "user_id": user.uuid,
            "session_id": session.uuid,
            "resume_id": resume.uuid,
            "resume_file_url": resume.file_path,
            "company_name": session.target_company or "Tech Company",
            "target_role": session.role or "Software Engineer",
            "current_difficulty": difficulty_num,
        }

    @staticmethod
    def _pending_interrupt(out: Any) -> Any | None:
        """Return the payload passed to interrupt(...), or None if the graph finished."""
        if isinstance(out, dict):
            interrupts = out.get("__interrupt__")
            if interrupts:
                first = interrupts[0]
                return getattr(first, "value", first)
        return None

    @staticmethod
    def _normalize_question(value: Any) -> dict:
        if hasattr(value, "model_dump"):
            value = value.model_dump()
        if isinstance(value, str):
            value = {"prompt": value}
        if not isinstance(value, dict):
            value = {"prompt": str(value)}
        prompt = (
            value.get("question_text")
            or value.get("prompt")
            or value.get("question")
            or value.get("text")
            or ""
        )
        raw_qtype = str(value.get("qtype") or value.get("type") or value.get("question_type") or "theory").lower()
        if raw_qtype in ("open_ended", "subjective", "conceptual", "theoretical"):
            normalized_qtype = "theory"
        elif "code" in raw_qtype or "coding" in raw_qtype:
            normalized_qtype = "coding"
        elif "mcq" in raw_qtype or "multiple_choice" in raw_qtype:
            normalized_qtype = "mcq"
        else:
            normalized_qtype = "theory"

        known = {"prompt", "question", "question_text", "text", "topic", "qtype", "type", "question_type",
                 "difficulty", "options", "question_id", "id", "rubric"}
        return {
            "prompt": str(prompt),
            "topic": str(value.get("topic") or "general"),
            "qtype": normalized_qtype,
            "difficulty": str(value.get("difficulty") or "medium"),
            "options": [str(o) for o in value["options"]] if isinstance(value.get("options"), list) else None,
            "meta": {k: v for k, v in value.items() if k not in known} or None,
        }

    @staticmethod
    def _extract_evaluation(out: Any) -> dict | None:
        ev = out.get("last_evaluation") if isinstance(out, dict) else None
        return ev if isinstance(ev, dict) else None

    @staticmethod
    def _extract_summary(out: Any) -> dict | None:
        if not isinstance(out, dict):
            return None
        s = out.get("summary") or out.get("final_report") or out.get("report")
        if hasattr(s, "model_dump"):
            s = s.model_dump()
        return s if isinstance(s, dict) else ({"text": str(s)} if s else None)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _cfg(session_uuid: str) -> dict:
        return {"configurable": {"thread_id": session_uuid}}

    async def _get_owned(self, user: UserModel, session_uuid: str) -> InterviewSessionModel:
        session = await self.sessions.get_one({"uuid": session_uuid, "user_uuid": user.uuid})
        if session is None:
            raise NotFoundException("Interview session")
        return session

    async def _mark_failed(self, session_uuid: str) -> None:
        await self.col.update_one(
            {"uuid": session_uuid}, {"$set": {"status": "failed", "updated_at": _now()}}
        )

    async def _apply_output(self, session_uuid: str, out: Any) -> InterviewTurnResponse:
        """Persist what the graph produced: either the next question or the final summary."""
        pending = self._pending_interrupt(out)
        if pending is not None:
            fields = self._normalize_question(pending)
            if not fields["prompt"]:
                await self._mark_failed(session_uuid)
                raise AppException("Interview engine returned an empty question", 502)
            doc = await self.col.find_one({"uuid": session_uuid}, {"turns": 1})
            seq = len(doc["turns"]) + 1
            turn = Turn(seq=seq, **fields)
            # $size guard => two concurrent requests can't both append the same seq
            updated = await self.col.find_one_and_update(
                {"uuid": session_uuid, "turns": {"$size": seq - 1}},
                {"$push": {"turns": turn.model_dump()}, "$set": {"updated_at": _now()}},
                return_document=ReturnDocument.AFTER,
            )
            if updated is None:
                raise ConflictException("Session changed concurrently, please retry")
            return InterviewTurnResponse(
                session_uuid=session_uuid,
                status=updated["status"],
                turn=TurnRead.model_validate(turn),
            )

        summary = self._extract_summary(out)
        updated = await self.col.find_one_and_update(
            {"uuid": session_uuid},
            {"$set": {"status": "completed", "summary": summary, "updated_at": _now()}},
            return_document=ReturnDocument.AFTER,
        )
        return InterviewTurnResponse(
            session_uuid=session_uuid, status=updated["status"], turn=None, summary=summary
        )

    # ------------------------------------------------------------------ public API
    async def start(self, user: UserModel, payload: InterviewCreate) -> InterviewTurnResponse:
        resume = await self.resumes.get_one({"uuid": payload.resume_uuid, "user_uuid": user.uuid})
        if resume is None:
            raise NotFoundException("Resume")
        if resume.status != "ready":
            raise ConflictException(f"Resume is not ready yet (status: {resume.status})")

        # Automatically auto-abandon any previous active session with 0 turns (crashed before 1st question)
        await self.col.update_many(
            {"user_uuid": user.uuid, "status": "active", "turns": {"$size": 0}},
            {"$set": {"status": "abandoned", "updated_at": _now()}},
        )

        active = await self.sessions.count({"user_uuid": user.uuid, "status": "active"})
        if active >= get_settings().MAX_ACTIVE_SESSIONS:
            raise ConflictException("Too many active interviews; finish or abandon one first")

        session = await self.sessions.create(
            InterviewSessionModel(
                user_uuid=user.uuid,
                resume_uuid=resume.uuid,
                role=payload.role,
                target_company=payload.target_company,
                difficulty=payload.difficulty,
            )
        )
        try:
            out = await self.graph.ainvoke(self._initial_state(user, session, resume), self._cfg(session.uuid))
            return await self._apply_output(session.uuid, out)
        except Exception:
            logger.exception("Graph failed while starting session %s", session.uuid)
            await self._mark_failed(session.uuid)
            raise AppException("Interview engine failed to start", 502)

    async def answer(self, user: UserModel, session_uuid: str, seq: int, text: str) -> InterviewTurnResponse:
        now = _now()
        # ONE atomic filtered update = ownership check + still active + question exists
        # + not answered yet (so client retries / double-submits get a clean 409).
        claimed = await self.col.find_one_and_update(
            {
                "uuid": session_uuid,
                "user_uuid": user.uuid,
                "status": "active",
                "turns": {"$elemMatch": {"seq": seq, "answer": None}},
            },
            {"$set": {"turns.$.answer": text, "turns.$.answered_at": now, "updated_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        if claimed is None:
            await self._get_owned(user, session_uuid)  # 404 if not theirs / doesn't exist
            raise ConflictException("Session is not active, or that question was already answered")

        try:
            out = await self.graph.ainvoke(Command(resume=text), self._cfg(session_uuid))
        except Exception:
            logger.exception("Graph failed while resuming session %s", session_uuid)
            # un-claim the answer so the user can simply retry
            await self.col.update_one(
                {"uuid": session_uuid, "turns": {"$elemMatch": {"seq": seq}}},
                {"$set": {"turns.$.answer": None, "turns.$.answered_at": None}},
            )
            raise AppException("Interview engine failed to process the answer", 502)

        evaluation = self._extract_evaluation(out)
        if evaluation:
            score = evaluation.get("score")
            await self.col.update_one(
                {"uuid": session_uuid, "turns": {"$elemMatch": {"seq": seq}}},
                {"$set": {
                    "turns.$.score": float(score) if isinstance(score, (int, float)) else None,
                    "turns.$.feedback": evaluation,
                }},
            )
        return await self._apply_output(session_uuid, out)

    async def get(self, user: UserModel, session_uuid: str) -> InterviewSessionModel:
        return await self._get_owned(user, session_uuid)

    async def list_for_user(self, user: UserModel, skip: int, limit: int) -> list[InterviewSessionModel]:
        return await self.sessions.find_many(
            {"user_uuid": user.uuid}, skip=skip, limit=limit, projection={"turns": 0}
        )

    async def abandon(self, user: UserModel, session_uuid: str) -> InterviewSessionModel:
        doc = await self.col.find_one_and_update(
            {"uuid": session_uuid, "user_uuid": user.uuid, "status": "active"},
            {"$set": {"status": "abandoned", "updated_at": _now()}},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            await self._get_owned(user, session_uuid)
            raise ConflictException("Only active sessions can be abandoned")
        return InterviewSessionModel.model_validate(doc)
