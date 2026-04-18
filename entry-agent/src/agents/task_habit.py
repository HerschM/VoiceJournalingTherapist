from typing import Optional

from livekit.agents import Agent, ChatContext, RunContext, function_tool

from tools.task_habit_tools import TaskHabitTools


class TaskHabitAgent(Agent):
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="""You are a productivity and habit tracking specialist. Your goal is to help the user be more productive and centered throughout the day.

            Key Responsibilities:
            1. Conduct morning ToDo chats to set the pace for the day.
            2. Schedule tasks and reminders.
            3. Schedule and track habits with specific metrics.

            Use the `create_task` tool to add new tasks or reminders.
            Use the `list_tasks` tool to review what's pending.
            Use the `log_habit` tool to track habit completion with metrics.

            Be encouraging, focused, and help the user stay on track with their goals.
            """,
            chat_ctx=chat_ctx,
            tools=[TaskHabitTools()]
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Introduce yourself as the Productivity Assistant and ask if the user wants to plan their day or log a habit.")

    @function_tool()
    async def return_to_orchestrator(self, context: RunContext):
        """Handoff back to the main assistant when the task/habit session is complete."""
        from agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Returning to main assistant"
