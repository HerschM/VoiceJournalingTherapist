from typing import Optional

from livekit.agents import Agent, ChatContext, RunContext, function_tool


class OrchestratorAgent(Agent):
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="""You are a powerful, voice-first productivity and wellness assistant. Your goal is to help the user be more productive and centered throughout the day.

            Key Responsibilities:
            1. Fast communication: Command around the app using voice.
            2. Offload thoughts: Free up working memory by offloading thoughts.
            3. Daily planning: Morning ToDo chats.
            4. Scheduling: Tasks, reminders, and habits.
            5. Reflection & Journaling: Journal thoughts and emotions at the end of the day.
            6. Wellness: Emotion management, therapy sessions, and guided meditation.

            You act as an orchestrator. Depending on the user's request, you should transfer them to specialized assistants.

            Specialized Assistants:
            - **Journaling & Reflection**: For offloading thoughts, daily reflection, and journaling.
            - **Productivity & Habits**: For ToDo chats, tasks, reminders, and habit tracking.
            - **Therapy & Emotions**: For emotion management, therapy sessions, and analyzing patterns.
            - **Guided Meditation**: For peaceful meditation sessions.

            Be helpful, efficient, and direct. Guide the user to the best assistant for their needs.
            """,
            chat_ctx=chat_ctx
        )

    async def on_enter(self) -> None:
        if not self.chat_ctx.items:
             await self.session.generate_reply(instructions="Greet the user warmly as their personal productivity and wellness assistant and ask how you can help them today.")

    @function_tool()
    async def transfer_to_journaling(self, context: RunContext):
        """Transfer the user to the Journaling and Reflection specialist."""
        from agents.journaling import JournalingAgent
        return JournalingAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Transferring to Journaling specialist"

    @function_tool()
    async def transfer_to_productivity(self, context: RunContext):
        """Transfer the user to the Productivity and Habits specialist."""
        from agents.task_habit import TaskHabitAgent
        return TaskHabitAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Transferring to Productivity specialist"

    @function_tool()
    async def transfer_to_therapy(self, context: RunContext):
        """Transfer the user to the Therapy and Emotion management specialist."""
        from agents.therapy import TherapyAgent
        return TherapyAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Transferring to Therapeutic specialist"

    @function_tool()
    async def transfer_to_meditation(self, context: RunContext):
        """Transfer the user to the Guided Meditation specialist."""
        from agents.meditation import MeditationAgent
        return MeditationAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Transferring to Meditation specialist"
