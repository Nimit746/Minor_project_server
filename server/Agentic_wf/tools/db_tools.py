from Agentic_wf.config.database import get_async_db
from typing import Dict, Any, Optional
from langchain_core.tools import tool


@tool
async def fetch_candidate_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a candidate's profile from the 'candidates' collection in MongoDB using their unique candidate_id. Returns the full profile document as a dictionary if found, otherwise returns None."""
    try:
        db = get_async_db()
        return await db.candidates.find_one({"candidate_id": candidate_id})
    except Exception as e:
        print(f'Error in fetch_candidate_profile: {e}')
        return None


@tool
async def save_or_update_candidate_profile(candidate_id: str, data: Dict[str, Any]) -> bool:
    """Saves or updates a candidate's profile in the 'candidates' collection in MongoDB. It uses the candidate_id to find the document and updates it with the provided data. If no profile is found, a new one is created (upsert=True)."""
    try:
        db = get_async_db()
        await db.candidates.update_one(
            {"candidate_id": candidate_id},
            {"$set": data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f'Error in save_or_update_candidate_profile: {e}')
        return False


@tool
async def record_session_history(candidate_id: str, session_data: Dict[str, Any]) -> bool:
    """Records a completed interview practice session in the 'sessions' collection in MongoDB. This is used to log the details of each session for historical analysis."""
    try:
        db = get_async_db()
        await db.sessions.insert_one({
            "candidate_id": candidate_id,
            **session_data
        })
        return True
    except Exception as e:
        print(f'Error in record_session_history: {e}')
        return False