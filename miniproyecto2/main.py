#olaolaolaolaolaolaolola   
import sys
import json
import uuid
import datetime
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from conexion_sftp import ConexionSFTP

# --- IMPORTACIÓN DIRECTA DE MINIJUEGOS ---
try:
    from minijuego_1 import jugar as jugar_blackjack
except ImportError:
    jugar_blackjack = None

try:
    from minijuego_2 import play_game_2 as jugar_encoder
except ImportError:
    jugar_encoder = None


RUTA_CONFIG = Path(__file__).with_name('config.json')

def cargar_config():
    with RUTA_CONFIG.open(encoding='utf-8') as archivo:
        return json.load(archivo)

def nuevo_event_id(player_id: str) -> str:
    """Genera un identificador único truncado basado en UUID4, como pidió el profesor."""
    return f"{player_id}-{uuid.uuid4().hex[:10]}"

def ejecutar_minijuego(game_id: int):
    """
    Ejecuta el minijuego correspondiente extrayendo 'Result' y 'Score',
    soportando tanto retornos en diccionario como en tupla.
    """
    resultado = "Lose"
    score = 0.0

    if game_id == 1 and jugar_blackjack:
        res = jugar_blackjack()
        if isinstance(res, tuple):
            resultado, score = res[0], res[1]
        elif isinstance(res, dict):
            resultado = res.get("Result", "Lose")
            score = res.get("Score", 0.0)

    elif game_id == 2 and jugar_encoder:
        res = jugar_encoder()
        if isinstance(res, tuple):
            resultado, score = res[0], res[1]
        elif isinstance(res, dict):
            resultado = res.get("Result", "Lose")
            score = res.get("Score", 0.0)
    else:
        print(f"[ADVERTENCIA] GameID {game_id} no reconocido o minijuego no disponible.")

    return str(resultado), float(score)


class ClienteLobby:
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.player_id = config['player_id']
        self.sftp = ConexionSFTP(config)
        
        self.archivos_procesados = set()
        
        # --- MÁQUINA DE ESTADOS ESTRICTA (COMO EN EL DIAGRAMA) ---
        self.estado = "INICIAL"
        self.join_enviado = False
        
        # Identificadores ACK (ReplyTo) para chequear confirmaciones
        self.join_id = None
        self.ready_id = None
        self.result_id = None
        
        # Cola de mensajes pendientes (para cuando llegan cosas fuera de orden)
        self.mensajes_pendientes = []

        # Polling continuo cada 300 ms
        self.timer_polling = QTimer()
        self.timer_polling.timeout.connect(self.loop_polling)

    def obtener_timestamp(self) -> str:
        return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()

    def enviar_mensaje(self, mensaje: dict) -> str:
        """Sube un diccionario JSON al servidor SFTP."""
        nombre_archivo = f"{mensaje['EventID']}.json"
        self.sftp.enviar_json(mensaje, nombre_archivo)
        return mensaje['EventID']

    def conectar_y_unirse(self):
        """Inicia la conexión y envía el Join obligatorio (solo una vez)."""
        if self.join_enviado:
            return

        try:
            print(f"[1] Conectando por SFTP al Host...")
            self.sftp.conectar()
            
            # --- EVENTO JOIN ---
            self.join_id = nuevo_event_id(self.player_id)
            mensaje_join = {
                "timestamp": self.obtener_timestamp(),
                "player_id": self.player_id,
                "Action": "Join",
                "EventID": self.join_id,
                "Stage": "Lobby"
            }
            
            print(f"[2] Enviando Join (EventID={self.join_id})...")
            self.enviar_mensaje(mensaje_join)
            
            self.join_enviado = True
            self.estado = "ESPERANDO_ACCEPTED"
            
            print("[3] Iniciando loop de escucha por polling...")
            self.timer_polling.start(300)
            
        except Exception as err:
            print(f"[ERROR DE CONEXIÓN]: {err}")

    def procesar_mensaje(self, msg: dict) -> bool:
        """
        Evalúa un mensaje en función del estado actual.
        Retorna True si fue procesado/descartado, y False si debe guardarse en la cola para después.
        """
        accion = msg.get("Action")
        reply_to = msg.get("ReplyTo")
        stage = msg.get("Stage", "R1")

        if accion == "Error":
            print(f"[ALERTA HOST ERROR]: {msg.get('Detail', 'Mensaje rechazado por el Host')}")
            return True

        # --- 1. ACK DE JOIN ---
        if accion == "Accepted":
            if self.estado == "ESPERANDO_ACCEPTED" and reply_to == self.join_id:
                print(f"[ESTADO] Join Aceptado. Jugador {self.player_id} en el Lobby. Esperando StageStart...")
                self.estado = "ESPERANDO_STAGE_START"
                return True
            return True

        # --- 2. STAGE START -> ENVIAMOS STAGE READY ---
        if accion == "StageStart":
            if self.estado in ["ESPERANDO_STAGE_START", "ESPERANDO_ASSIGN", "INICIAL"]:
                print(f"[ESTADO] Evento StageStart recibido para la etapa {stage}.")
                self.ready_id = nuevo_event_id(self.player_id)
                mensaje_ready = {
                    "timestamp": self.obtener_timestamp(),
                    "player_id": self.player_id,
                    "Action": "StageReady",
                    "EventID": self.ready_id,
                    "Stage": stage
                }
                print(f" -> Enviando StageReady (EventID={self.ready_id})...")
                self.enviar_mensaje(mensaje_ready)
                self.estado = "ESPERANDO_STAGE_READY_ACCEPTED"
                return True
            return False

        # --- 3. STAGE READY ACCEPTED ---
        if accion == "StageReadyAccepted":
            if self.estado == "ESPERANDO_STAGE_READY_ACCEPTED" and reply_to == self.ready_id:
                print(f"[ESTADO] StageReadyAccepted confirmado. Esperando StageActive...")
                self.estado = "ESPERANDO_STAGE_ACTIVE"
                return True
            return False

        # --- 4. STAGE ACTIVE (INICIA BUCLE DE JUEGOS) ---
        if accion == "StageActive":
            if self.estado in ["ESPERANDO_STAGE_ACTIVE", "ESPERANDO_STAGE_READY_ACCEPTED"]:
                print(f"[ESTADO] ¡Etapa {stage} ACTIVA! El cliente ahora espera asignaciones...")
                self.estado = "ESPERANDO_ASSIGN"
                return True
            return False

        # --- 5. ASSIGN -> JUGAR -> ENVIAR RESULT ---
        if accion == "Assign":
            if self.estado != "ESPERANDO_ASSIGN":
                # Si llega cuando el jugador está jugando o no está listo, lo mandamos a la cola
                return False

            try:
                game_id = msg["GameID"]
                attempt = msg["Attempt"]
            except KeyError as e:
                print(f"[ERROR] Mensaje 'Assign' inválido. Falta: {e}")
                return True

            print(f"\n==========================================")
            print(f"[NUEVO TURNO] Asignado GameID={game_id} | Attempt={attempt} | Stage={stage}")
            print(f"==========================================")

            # Detener el reloj de descargas para que el juego ande fluido
            self.timer_polling.stop()
            res, score = ejecutar_minijuego(game_id)
            self.timer_polling.start(300)

            self.result_id = nuevo_event_id(self.player_id)
            mensaje_result = {
                "timestamp": self.obtener_timestamp(),
                "player_id": self.player_id,
                "Action": "Result",
                "EventID": self.result_id,
                "Stage": stage,
                "GameID": game_id,
                "Attempt": attempt,
                "Result": str(res),
                "Score": float(score)
            }
            
            print(f"[RESULTADO] Enviando Result: {res} | Score: {score}")
            self.enviar_mensaje(mensaje_result)
            self.estado = "ESPERANDO_RESULT_ACK"
            return True

        # --- 6. RESULT ACCEPTED (CERRAMOS EL CICLO Y VOLVEMOS A ESPERAR JUEGO) ---
        if accion == "ResultAccepted":
            if self.estado == "ESPERANDO_RESULT_ACK" and reply_to == self.result_id:
                print(f"[ACK] ¡El servidor confirmó el puntaje! Listo para el siguiente minijuego.\n")
                
                # LA CLAVE DE TODO: Regresamos el estado a ESPERANDO_ASSIGN para seguir infinitamente
                self.estado = "ESPERANDO_ASSIGN"
                self.result_id = None
                return True
            return False

        # --- 7. EVENTOS DE CIERRE ---
        if accion in ["Eliminated", "GameOver"]:
            print(f"\n[FIN DE PARTIDA] El Host envió el evento: {accion}. Cerrando cliente.")
            self.timer_polling.stop()
            self.app.quit()
            return True

        return True

    def procesar_pendientes(self):
        """Intenta ejecutar los mensajes que estaban guardados en la cola temporal."""
        if not self.mensajes_pendientes:
            return

        pendientes_restantes = []
        for msg in self.mensajes_pendientes:
            procesado = self.procesar_mensaje(msg)
            if not procesado:
                pendientes_restantes.append(msg)
        
        self.mensajes_pendientes = pendientes_restantes

    def loop_polling(self):
        """Bucle principal asíncrono que corre cada 300 ms."""
        nuevos_archivos = self.sftp.leer_nuevos_json(self.archivos_procesados)
        
        mensajes_a_procesar = []
        
        # 1. Registrar archivos leídos
        for file_name, msg in nuevos_archivos:
            self.archivos_procesados.add(file_name)
            mensajes_a_procesar.append(msg)

        # 2. ORDEN CRONOLÓGICO PARA QUE EL SERVIDOR NO SE MAREE (Soluciona el error del GameID)
        mensajes_a_procesar.sort(key=lambda x: x.get("timestamp", ""))

        # 3. Procesar en orden estricto
        for msg in mensajes_a_procesar:
            procesado = self.procesar_mensaje(msg)
            if not procesado:
                self.mensajes_pendientes.append(msg)

        # 4. Revisar la cola
        self.procesar_pendientes()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    try:
        config = cargar_config()
    except Exception as e:
        print(f"[ERROR DE CONFIGURACIÓN]: No se pudo cargar config.json: {e}")
        return 1

    cliente = ClienteLobby(app, config)
    cliente.conectar_y_unirse()
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())