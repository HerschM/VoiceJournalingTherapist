import logging
from typing import Optional, TypedDict

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
from livekit.plugins import ai_coustics, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agents.orchestrator import OrchestratorAgent
from db import supabase

logger = logging.getLogger("agent")

load_dotenv(".env.local")

class SessionUserData(TypedDict):
    user_id: str
    session_id: Optional[str]

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


async def create_supabase_session(user_id: str, room_id: str, call_type: str = "catch_up") -> str:
    """Creates a new session record in Supabase."""
    data = {
        "user_id": user_id,
        "livekit_room_id": room_id,
        "type": call_type,
        "status": "in_progress",
        "started_at": "now()"
    }
    try:
        response = supabase.table("call_sessions").insert(data).execute()
        return response.data[0]['id']
    except Exception as e:
        logger.error(f"Error creating supabase session: {e}")
        return ""


@server.rtc_session(agent_name="entry-agent")
async def my_agent(ctx: JobContext):
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # In a real app, you'd get the user_id from participant metadata or auth token
    # For now, we'll use a placeholder or check room metadata
    user_id = ctx.room.metadata or "8e71cdda-0475-40f5-9da9-a73ffee906ce" # Placeholder UUID

    session_id = await create_supabase_session(user_id, ctx.room.name)

    # Set up a voice AI pipeline
    session = AgentSession[SessionUserData](
        stt=inference.STT(model="deepgram/nova-3", language="multi"),
        llm=inference.LLM(model="openai/gpt-4o-mini"), # Using a standard model name
        tts=inference.TTS(
            model="cartesia/sonic", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        userdata={"user_id": user_id, "session_id": session_id}
    )

    # Start the session
    await session.start(
        agent=OrchestratorAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else ai_coustics.audio_enhancement(
                        model=ai_coustics.EnhancerModel.QUAIL_VF_L
                    )
                ),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Update session status when disconnected
    @ctx.room.on("disconnected")
    def on_disconnected(_):
        if session_id:
            try:
                supabase.table("call_sessions").update({
                    "status": "completed",
                    "ended_at": "now()"
                }).eq("id", session_id).execute()
            except Exception as e:
                logger.error(f"Error updating session status: {e}")



if __name__ == "__main__":
    cli.run_app(server)
