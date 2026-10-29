"""Prueba básica para verificar la conexión SSH/SFTP con el host central."""

import json
from pathlib import Path

from conexion_host import ConexionHost


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.parent / "config_grupo.json"


def cargar_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def main():
    config = cargar_config()
    conexion = ConexionHost(config)

    try:
        conexion.conectar()

        if conexion.verificar_conexion():
            print("Conexión SSH/SFTP establecida correctamente.")
            print(f"PlayerID: {config['player_id']}")
            print(f"Usuario:  {config['username']}")
            print(f"Host:     {config['host']}:{config['port']}")
            print(f"Inbox:    {config['remote_inbox']}")
            print(f"Outbox:   {config['remote_outbox']}")
        else:
            print("No fue posible verificar la conexión SSH/SFTP.")

    finally:
        conexion.cerrar_conexion()


if __name__ == "__main__":
    main()
