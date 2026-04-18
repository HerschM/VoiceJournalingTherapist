from typing import Optional

from livekit.agents import Agent, ChatContext, RunContext, function_tool

from tools.journal_tools import JournalTools


class JournalingAgent(Agent, JournalTools):
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="""You are a journaling and reflection specialist. Your goal is to help the user offload top-of-mind thoughts, reflect on their day, and journal their emotions.

            Key Responsibilities:
            1. Help offload thoughts to free up working memory.
            2. Revisit thoughts when the user is free.
            3. Reflect on the day's events and journal emotions.

            Use the `save_thought` tool for quick offloads.
            Use the `save_journal_entry` tool at the end of a reflection session.

            Be empathetic, supportive, and encourage deep reflection.
            """,
            chat_ctx=chat_ctx,
        )
    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Introduce yourself as the Journaling Assistant and ask what's on the user's mind or if they'd like to reflect on their day.")

    @function_tool()
    async def return_to_orchestrator(self, context: RunContext):
        """Handoff back to the main assistant when the journaling session is complete."""
        from agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Returning to main assistant"
