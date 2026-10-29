"""Estado local recomendado para organizar la ejecución del cliente del jugador."""

from dataclasses import dataclass
from typing import Any


@dataclass
class EstadoJuego:
    stage: str = "Lobby"
    game_id: int | None = None
    attempt: int | None = None
    sabotage: dict[str, Any] | None = None
    game_over: bool = False

    def actualizar_desde_host(self, mensaje: dict[str, Any]) -> None:
        """Actualiza datos generales necesarios para organizar el flujo local."""
        if "Stage" in mensaje:
            self.stage = str(mensaje["Stage"])

        # TODO:
        # Agregar aquí otros estados locales que resulte conveniente mantener.
        # Las variables globales del juego son administradas por el host central.
