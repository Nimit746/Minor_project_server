from Agentic_wf.config.database import get_async_db
from typing import Dict, Any, Optional


async def fetch_candidate_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Fetch candidate profile from MongoDB."""
    try:
        db = get_async_db()
        return await db.candidates.find_one({"candidate_id": candidate_id})
    except Exception as e:
        print(f'Error in fetch_candidate_profile: {e}')
        return None


async def save_or_update_candidate_profile(candidate_id: str, data: Dict[str, Any]) -> bool:
    """Save or update candidate profile in MongoDB."""
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


async def record_session_history(candidate_id: str, session_data: Dict[str, Any]) -> bool:
    """Record a completed interview practice session in MongoDB."""
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
