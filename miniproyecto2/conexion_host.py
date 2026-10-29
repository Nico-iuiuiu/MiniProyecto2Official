import json
import os
import posixpath
import re
import tempfile
import uuid
from pathlib import Path

import paramiko


class ConexionHost:
    def __init__(self, config: dict):
        self.host = config['host']
        self.port = int(config.get('port', 22))
        self.username = config['username']
        self.password = config['password']
        self.remote_inbox = config.get('remote_inbox', '/inbox')
        self.remote_outbox = config.get('remote_outbox', '/outbox')
        self.trust_host_key = config.get('trust_host_key', False)
        self.ssh = None
        self.sftp = None
        self.mensajes_leidos = set()

    def conectar(self):
        self.cerrar_conexion()
        cliente = paramiko.SSHClient()
        cliente.load_system_host_keys()
        # Solo habilitar AutoAddPolicy si se ha confirmado la huella del servidor.
        cliente.set_missing_host_key_policy(
            paramiko.AutoAddPolicy() if self.trust_host_key else paramiko.RejectPolicy()
        )
        try:
            cliente.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                auth_timeout=10,
                banner_timeout=10,
                look_for_keys=False,
                allow_agent=False,
            )
            sftp = cliente.open_sftp()
        except Exception:
            cliente.close()
            raise
        self.ssh = cliente
        self.sftp = sftp
        return True

    def cerrar_conexion(self):
        if self.sftp is not None:
            try:
                self.sftp.close()
            finally:
                self.sftp = None
        if self.ssh is not None:
            try:
                self.ssh.close()
            finally:
                self.ssh = None

    def verificar_conexion(self):
        transporte = self.ssh.get_transport() if self.ssh else None
        return bool(self.sftp is not None and transporte and transporte.is_active() and transporte.is_authenticated())

    def enviar_json(self, mensaje: dict):
        if not self.verificar_conexion():
            raise ConnectionError('No existe una conexión SSH/SFTP activa')
        if not isinstance(mensaje, dict):
            raise TypeError('El mensaje debe ser un diccionario')
        mensaje = dict(mensaje)
        mensaje.setdefault('EventID', str(uuid.uuid4()))
        identificador = re.sub(r'[^A-Za-z0-9_-]', '_', str(mensaje['EventID']))[:80]
        nombre = f'{identificador}_{uuid.uuid4().hex}.json'
        destino = posixpath.join(self.remote_inbox, nombre)
        temporal_remoto = destino + '.part'
        ruta_local = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json',
                                             delete=False) as archivo:
                ruta_local = archivo.name
                json.dump(mensaje, archivo, ensure_ascii=False, indent=2)
            self.sftp.put(ruta_local, temporal_remoto)
            self.sftp.rename(temporal_remoto, destino)  # Publicación solo tras subir completo
            return nombre
        finally:
            if ruta_local:
                Path(ruta_local).unlink(missing_ok=True)
            # No se borra .part remoto: si la transferencia falló, puede limpiarse por separado.

    def leer_nuevos_json(self):
        if not self.verificar_conexion():
            raise ConnectionError('No existe una conexión SSH/SFTP activa')
        mensajes = []
        for nombre in sorted(self.sftp.listdir(self.remote_outbox)):
            if not nombre.endswith('.json') or nombre in self.mensajes_leidos:
                continue
            ruta = posixpath.join(self.remote_outbox, nombre)
            try:
                with self.sftp.open(ruta, 'r') as archivo:
                    mensaje = json.loads(archivo.read().decode('utf-8'))
                if not isinstance(mensaje, dict):
                    raise ValueError('El JSON recibido no es un objeto')
            except (OSError, ValueError, UnicodeError) as exc:
                print(f'[SFTP] No se pudo leer {nombre}: {exc}')
                continue  # Permite reintentar posteriormente
            self.mensajes_leidos.add(nombre)
            mensajes.append(mensaje)
        return mensajes
