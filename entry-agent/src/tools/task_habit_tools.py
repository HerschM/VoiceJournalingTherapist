import logging
from typing import Any, Optional

from livekit.agents import RunContext, function_tool

from db import supabase

logger = logging.getLogger("task_habit_tools")

class TaskHabitTools:
    @function_tool()
    async def create_task(
        self,
        context: RunContext,
        title: str,
        description: Optional[str] = None,
        scheduled_for: Optional[str] = None
    ):
        """Creates a new task or reminder for the user.

        Args:
            title: The title of the task.
            description: Detailed description of the task.
            scheduled_for: ISO 8601 timestamp for when the task is scheduled.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "scheduled_for": scheduled_for,
            "status": "pending"
        }
        try:
            response = supabase.table("tasks").insert(data).execute()
            return f"Task '{title}' created successfully. ID: {response.data[0]['id']}"
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return f"Failed to create task: {e!s}"

    @function_tool()
    async def list_tasks(self, context: RunContext, status: Optional[str] = "pending"):
        """Lists tasks for the user, filtered by status.

        Args:
            status: Filter tasks by status ('pending', 'completed', etc.)
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            query = supabase.table("tasks").select("*").eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
            response = query.execute()
            if not response.data:
                return "No tasks found."
            tasks_str = "\n".join([f"- {t['title']} (ID: {t['id']}, Scheduled: {t['scheduled_for']})" for t in response.data])
            return f"Your tasks:\n{tasks_str}"
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return f"Failed to list tasks: {e!s}"

    @function_tool()
    async def log_habit(
        self,
        context: RunContext,
        habit_name: str,
        metrics: dict[str, Any],
        session_id: Optional[str] = None
    ):
        """Logs a habit entry with specific metrics.

        Args:
            habit_name: The name of the habit (e.g., 'Gym', 'Sleep').
            metrics: A dictionary of metrics for the habit (e.g., {'reps': 10, 'weight': 135}).
            session_id: The current call session ID.
        """
        user_id = context.userdata.get("user_id")
        if not user_id:
            return "Error: User ID not found."

        try:
            # First, find or create the habit
            habit_resp = supabase.table("habits").select("id").eq("user_id", user_id).eq("name", habit_name).execute()
            if not habit_resp.data:
                habit_resp = supabase.table("habits").insert({"user_id": user_id, "name": habit_name}).execute()

            habit_id = habit_resp.data[0]['id']

            # Then log the habit
            log_data = {
                "user_id": user_id,
                "habit_id": habit_id,
                "session_id": session_id,
                "metrics": metrics
            }
            response = supabase.table("habit_logs").insert(log_data).execute()
            return f"Habit '{habit_name}' logged successfully. ID: {response.data[0]['id']}"
        except Exception as e:
            logger.error(f"Error logging habit: {e}")
            return f"Failed to log habit: {e!s}"
