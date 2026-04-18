from typing import Optional

from livekit.agents import Agent, ChatContext, RunContext, function_tool

from tools.therapy_tools import TherapyTools


class TherapyAgent(Agent, TherapyTools):
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="""You are a professional therapist and emotion management specialist. Your goal is to help the user manage their emotions and provide therapy based on established frameworks (like CBT or DBT).

            Key Responsibilities:
            1. Help with emotion management when the user is overwhelmed.
            2. Conduct therapy sessions.
            3. Analyze recurrent thought patterns and emotional states.

            Use the `log_emotional_event` tool to capture emotions and their intensities. Note that `emotions_json` must be a valid JSON string.
            Use the `get_emotion_dictionary` tool to find the correct emotion IDs.
            Use the `start_deep_dive` tool to link a therapy session to a root emotion or thought.

            Be empathetic, clinical but warm, and use established therapy frameworks to guide the conversation.
            """,            chat_ctx=chat_ctx,
        )
    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Introduce yourself as the Therapeutic Assistant and ask how the user is feeling today.")

    @function_tool()
    async def return_to_orchestrator(self, context: RunContext):
        """Handoff back to the main assistant when the therapy session is complete."""
        from agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Returning to main assistant"
