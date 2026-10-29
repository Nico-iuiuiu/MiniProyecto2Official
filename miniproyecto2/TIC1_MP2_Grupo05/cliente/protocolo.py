"""Funciones de apoyo para construir e interpretar los mensajes del protocolo del juego."""

from datetime import datetime
import uuid


def nuevo_event_id(player_id: str) -> str:
    """Genera un identificador único para un mensaje enviado por el jugador."""
    return f"{player_id}-{uuid.uuid4().hex[:10]}"


def mensaje_base(player_id: str, action: str, stage: str | None = None) -> dict:
    """Crea los campos comunes de un mensaje enviado al host central."""
    mensaje = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "PlayerID": player_id,
        "Action": action,
        "EventID": nuevo_event_id(player_id),
    }

    if stage is not None:
        mensaje["Stage"] = stage

    return mensaje


def crear_join(player_id: str, test_stage: str | None = None) -> dict:
    """Ejemplo completo de construcción de un mensaje Join."""
    mensaje = mensaje_base(player_id, "Join")

    if test_stage in {"R1", "R2", "Final"}:
        mensaje["TestStage"] = test_stage

    return mensaje


def crear_result(
    player_id: str,
    stage: str,
    game_id: int,
    attempt: int,
    result: str,
    score: float,
) -> dict:
    """Ejemplo completo de construcción de un mensaje Result."""
    mensaje = mensaje_base(player_id, "Result", stage)
    mensaje["GameID"] = game_id
    mensaje["Attempt"] = attempt
    mensaje["Result"] = result
    mensaje["Score"] = score
    return mensaje


# TODO:
# Incluir idealmente funciones para todos los mensajes enviados o recibidos
# que necesiten ser construidos o interpretados por el cliente.
#
# Mensajes enviados por el jugador:
# - Join
# - StageReady
# - Result
# - Recover
#
# Mensajes recibidos desde el host central:
# - Accepted
# - StageStart
# - FinalStart
# - StageReadyAccepted
# - StageActive
# - Assign
# - Sabotage
# - ResultAccepted
# - RecoverAccepted
# - Eliminated
# - GameOver
# - Error
# - TestStageComplete
