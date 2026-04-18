import logging
from typing import Optional

from livekit.agents import RunContext, function_tool

from db import supabase

logger = logging.getLogger("journal_tools")

class JournalTools:
    @function_tool()
    async def save_journal_entry(
        self,
        context: RunContext,
        transcript: str,
        summary: str,
        session_id: Optional[str] = None
    ):
        """Saves a journal entry to the database.
        Use this after a reflection session or when the user wants to journal their day.

        Args:
            transcript: The full transcript of the conversation.
            summary: A summary of the journal entry.
            session_id: The session ID from the database.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found in session userdata."

        data = {
            "user_id": user_id,
            "session_id": session_id,
            "transcript": transcript,
            "summary": summary,
        }
        try:
            response = supabase.table("journal_entries").insert(data).execute()
            return f"Journal entry saved successfully. ID: {response.data[0]['id']}"
        except Exception as e:
            logger.error(f"Error saving journal entry: {e}")
            return f"Failed to save journal entry: {e!s}"

    @function_tool()
    async def save_thought(
        self,
        context: RunContext,
        content: str,
        session_id: str,
        embedding: Optional[list[float]] = None
    ):
        """Saves a single thought to the database for future retrieval or analysis.
        Use this when the user 'offloads' a top-of-mind thought.

        Args:
            content: The content of the thought.
            session_id: The session ID from the database.
            embedding: The embedding vector of the thought content.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found in session userdata."

        data = {
            "user_id": user_id,
            "session_id": session_id,
            "thought_content": content,
            "embedding": embedding,
        }
        try:
            response = supabase.table("thoughts").insert(data).execute()
            return f"Thought saved successfully. ID: {response.data[0]['id']}"
        except Exception as e:
            logger.error(f"Error saving thought: {e}")
            return f"Failed to save thought: {e!s}"

    @function_tool()
    async def get_recent_thoughts(self, context: RunContext, limit: int = 10):
        """Fetches recent thoughts for the user to revisit.

        Args:
            limit: The number of recent thoughts to fetch.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            response = (
                supabase.table("thoughts")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            if not response.data:
                return "No recent thoughts found."

            thoughts_str = "\n".join([f"- {t['thought_content']} (Date: {t['created_at']})" for t in response.data])
            return f"Recent Thoughts:\n{thoughts_str}"
        except Exception as e:
            logger.error(f"Error fetching thoughts: {e}")
            return f"Failed to fetch thoughts: {e!s}"

