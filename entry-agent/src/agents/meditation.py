from typing import Optional

from livekit.agents import (
    Agent,
    AudioConfig,
    BackgroundAudioPlayer,
    BuiltinAudioClip,
    ChatContext,
    RunContext,
    function_tool,
)


class MeditationAgent(Agent):
    def __init__(self, chat_ctx: Optional[ChatContext] = None):
        super().__init__(
            instructions="""You are a meditation guide. Your goal is to lead the user through a peaceful guided meditation session.

            Key Responsibilities:
            1. Provide a calming, slow-paced guided meditation.
            2. Encourage mindful breathing and relaxation.
            3. Use the peaceful background music (Forest Ambience) to enhance the experience.

            Be very calm, speak slowly with frequent pauses, and use soothing language.
            """,
            chat_ctx=chat_ctx
        )
        self.background_audio = BackgroundAudioPlayer(
            ambient_sound=AudioConfig(BuiltinAudioClip.FOREST_AMBIENCE, volume=0.3)
        )

    async def on_enter(self) -> None:
        # Start the background audio when entering the meditation agent
        await self.background_audio.start(room=self.session.room, agent_session=self.session)
        await self.session.generate_reply(instructions="Introduce yourself in a very soft, calming voice and ask if the user is ready to begin their guided meditation.")

    async def aclose(self) -> None:
        await self.background_audio.aclose()
        await super().aclose()

    @function_tool()
    async def stop_meditation(self, context: RunContext):
        """Stops the meditation session and returns to the main assistant."""
        await self.background_audio.aclose()
        from agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent(chat_ctx=self.chat_ctx.copy(exclude_instructions=True)), "Stopping meditation and returning to main assistant"
