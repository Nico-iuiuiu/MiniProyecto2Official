"""Estructura principal recomendada para integrar el cliente completo del juego."""

import time


INTERVALO_POLLING = 0.2


def main():
    # TODO:
    # Cargar la configuración del grupo.
    # Crear la conexión con el host central.
    # Realizar el ingreso al Lobby.
    # Inicializar el estado local del juego.

    while True:
        # TODO:
        # Consultar periódicamente los mensajes nuevos disponibles en /outbox.
        # Procesar cada mensaje según Action y Stage.
        # Ejecutar los minijuegos o acciones que correspondan.
        # Enviar al host central los mensajes generados por el jugador.
        # Finalizar el ciclo cuando termine la partida.
        time.sleep(INTERVALO_POLLING)


if __name__ == "__main__":
    main()
