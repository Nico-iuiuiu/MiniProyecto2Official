"""Estructura recomendada para gestionar la comunicación SSH/SFTP con el host central."""

import json
from pathlib import Path

import paramiko


class ConexionHost:
    def __init__(self, config: dict):
        self.host = config["host"]
        self.port = config.get("port", 22)
        self.username = config["username"]
        self.password = config["password"]
        self.remote_inbox = config.get("remote_inbox", "/inbox")
        self.remote_outbox = config.get("remote_outbox", "/outbox")

        self.ssh = None
        self.sftp = None
        self.mensajes_leidos = set()

    def conectar(self):
        """Establece la conexión SSH y abre el canal SFTP."""
        # TODO:
        # Crear el cliente SSH con Paramiko.
        # Configurar la política de claves del host.
        # Conectarse utilizando host, puerto, usuario y contraseña.
        # Abrir el canal SFTP.
        pass

    def cerrar_conexion(self):
        """Cierra de forma ordenada las conexiones SFTP y SSH."""
        # TODO:
        # Cerrar primero el canal SFTP y luego la conexión SSH.
        pass

    def verificar_conexion(self):
        """Comprueba si la conexión SSH/SFTP se encuentra disponible."""
        # TODO:
        # Retornar True cuando la conexión se encuentre activa y False en caso contrario.
        pass

    def enviar_json(self, mensaje: dict):
        """Transfiere un mensaje JSON al directorio /inbox del host central."""
        # TODO:
        # Generar un nombre de archivo único a partir de EventID.
        # Guardar temporalmente el diccionario como archivo .json.
        # Transferir el archivo mediante SFTP hacia remote_inbox.
        # Evitar que el host lea un archivo mientras todavía se está transfiriendo.
        pass

    def leer_nuevos_json(self):
        """Lee los mensajes JSON nuevos disponibles en /outbox."""
        # TODO:
        # Listar los archivos disponibles en remote_outbox.
        # Identificar cuáles todavía no han sido procesados.
        # Descargar y convertir cada archivo JSON a un diccionario.
        # Registrar los archivos ya leídos para evitar procesarlos dos veces.
        # Retornar una lista con los mensajes nuevos.
        pass
