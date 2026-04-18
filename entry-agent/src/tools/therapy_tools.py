import logging
from typing import Optional

from livekit.agents import RunContext, function_tool

from db import supabase

logger = logging.getLogger("therapy_tools")

class TherapyTools:
    @function_tool()
    async def log_emotional_event(
        self,
        context: RunContext,
        session_id: str,
        emotions_json: str,
        summary: Optional[str] = None,
    ):
        """Logs an emotional event with specific intensities for various emotions.

        Args:
            session_id: The current call session ID.
            emotions_json: A JSON string list of objects with 'emotion_id' and 'intensity' (0.0 to 1.0). (e.g., '[{"emotion_id": "joy", "intensity": 0.8}]')
            summary: A brief context or summary of the emotional event.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            import json
            emotions = json.loads(emotions_json)
            # 1. Create the emotional event
            event_data = {
                "user_id": user_id,
                "session_id": session_id,
                "context_summary": summary,
            }
            event_resp = supabase.table("emotional_events").insert(event_data).execute()
            event_id = event_resp.data[0]["id"]

            # 2. Add emotion scores
            for emotion in emotions:
                score_data = {
                    "event_id": event_id,
                    "emotion_id": emotion["emotion_id"],
                    "intensity": emotion["intensity"],
                }
                supabase.table("event_emotion_scores").insert(score_data).execute()

            return f"Emotional event logged successfully. ID: {event_id}"
        except Exception as e:
            logger.error(f"Error logging emotional event: {e}")
            return f"Failed to log emotional event: {e!s}"


    @function_tool()
    async def get_emotion_dictionary(self, context: RunContext):
        """Fetches the available emotions and their IDs from the dictionary."""
        try:
            response = supabase.table("emotion_dictionary").select("*").execute()
            if not response.data:
                return "No emotions found in dictionary."
            emotions_str = "\n".join([f"- {e['display_name']} (ID: {e['id']}, Category: {e['category']})" for e in response.data])
            return f"Available Emotions:\n{emotions_str}"
        except Exception as e:
            logger.error(f"Error fetching emotion dictionary: {e}")
            return f"Failed to fetch emotion dictionary: {e!s}"

    @function_tool()
    async def start_deep_dive(
        self,
        context: RunContext,
        session_id: str,
        root_emotion_id: Optional[str] = None,
        root_thought_id: Optional[str] = None,
    ):
        """Initializes a therapist deep dive session linked to a specific emotion or thought.

        Args:
            session_id: The current call session ID.
            root_emotion_id: The ID of the emotion being explored (UUID).
            root_thought_id: The ID of the thought being explored (UUID).
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            data = {
                "user_id": user_id,
                "session_id": session_id,
                "root_emotion_id": root_emotion_id,
                "root_thought_id": root_thought_id,
            }
            response = supabase.table("therapist_deep_dives").insert(data).execute()
            return f"Therapist deep dive initiated. ID: {response.data[0]['id']}"
        except Exception as e:
            logger.error(f"Error starting deep dive: {e}")
            return f"Failed to start deep dive: {e!s}"

    @function_tool()
    async def get_recent_emotional_events(self, context: RunContext, limit: int = 5):
        """Fetches recent emotional events for the user to analyze patterns.

        Args:
            limit: The number of recent events to fetch.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            response = (
                supabase.table("emotional_events")
                .select("*, event_emotion_scores(*, emotion_dictionary(*))")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            if not response.data:
                return "No recent emotional events found."

            events_summary = []
            for event in response.data:
                emotions = [f"{score['emotion_dictionary']['display_name']} ({score['intensity']})" for score in event['event_emotion_scores']]
                events_summary.append(f"- Date: {event['created_at']}, Emotions: {', '.join(emotions)}, Summary: {event['context_summary']}")

            return "Recent Emotional Events:\n" + "\n".join(events_summary)
        except Exception as e:
            logger.error(f"Error fetching recent emotional events: {e}")
            return f"Failed to fetch recent emotional events: {e!s}"

