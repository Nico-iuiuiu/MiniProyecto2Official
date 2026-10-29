"""Estructura de prueba recomendada para validar una etapa del juego sin modificar main.py."""

import json
from pathlib import Path

from conexion_host import ConexionHost


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent / "config_grupo.json"

# Cambiar este valor para solicitar otra etapa al host de pruebas.
ETAPA_PRUEBA = "R1"


def cargar_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def probar_ronda_1():
    config = cargar_config()
    conexion = ConexionHost(config)

    # Secuencia recomendada de funciones para probar R1:
    #
    # conexion.conectar()
    # enviar_join(test_stage="R1")
    # esperar_accepted()
    # esperar_stage_start()
    # enviar_stage_ready()
    # esperar_stage_ready_accepted()
    # esperar_stage_active()
    #
    # while ronda_1_activa():
    #     assign = esperar_assign()
    #     result, score = ejecutar_minijuego(assign)
    #     enviar_result(assign, result, score)
    #     esperar_result_accepted()
    #
    # esperar_test_stage_complete()
    # conexion.cerrar_conexion()
    #
    # TODO:
    # Implementar las funciones anteriores reutilizando conexion_host.py,
    # protocolo.py, estado_juego.py y los minijuegos desarrollados por el grupo.
    pass


if __name__ == "__main__":
    probar_ronda_1()
