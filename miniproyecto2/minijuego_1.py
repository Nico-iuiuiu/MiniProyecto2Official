"""Plantilla recomendada para un minijuego utilizado durante R1 y R2."""
import sys
import os
import random
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton
from PySide6.QtGui import QPixmap 
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QEventLoop
from ventana import Ui_Dialog 

class JuegoBlackjack(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.lbl_carta.setVisible(False)
        self.lbl_carta_dealer.setVisible(False)
        
        # --- MAZO VISUAL ---
        self.lbl_mazo = QLabel(self)
        ancho = self.lbl_carta.width() if self.lbl_carta.width() > 10 else 90
        alto = self.lbl_carta.height() if self.lbl_carta.height() > 10 else 130
        self.lbl_mazo.setGeometry(30, 30, ancho, alto)
        self.lbl_mazo.setScaledContents(True)
        
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_reverso = os.path.join(ruta_actual, "Cards (large)", "card_back.png")
        
        if os.path.exists(ruta_reverso):
            self.lbl_mazo.setPixmap(QPixmap(ruta_reverso))
        else:
            self.lbl_mazo.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            self.lbl_mazo.setText("MAZO")
            self.lbl_mazo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mazo.show()
        
        # --- BOTÓN DOBLE O NADA ---
        self.btn_doble = QPushButton("¡DOBLE O NADA! (200 pts)", self)
        self.btn_doble.setGeometry(280, 250, 240, 50)
        self.btn_doble.setStyleSheet(
            "background-color: #FFD700; color: black; font-weight: bold; "
            "font-size: 16px; border-radius: 10px; border: 2px solid white;"
        )
        self.btn_doble.setVisible(False)
        self.btn_doble.clicked.connect(self.jugar_doble_o_nada)

        self.mano_jugador = []
        self.mano_dealer = []
        
        self.juego_terminado = False
        self.esperando_doble = False
        self.en_doble_o_nada = False  
        
        # Variables finales exigidas por el profe
        self.puntos_recompensa = 0    
        self.estado_final = "Lose"

        self.puntaje_jugador = 0
        self.ases_jugador = 0
        self.puntaje_dealer = 0
        self.ases_dealer = 0
        
        self.valores_cartas = {
            "02": 2, "03": 3, "04": 4, "05": 5, "06": 6, 
            "07": 7, "08": 8, "09": 9, "10": 10,
            "J": 10, "Q": 10, "K": 10, "A": 11
        }
        
        self.tiempo_restante = 15
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        
        self.btn_pedir.clicked.connect(self.pedir_carta)
        self.btn_plantar.clicked.connect(self.plantarse)

        QTimer.singleShot(100, self.iniciar_partida_global)

    def animar_carta(self, label, punto_destino):
        punto_inicio = self.lbl_mazo.pos()
        label.move(punto_inicio)
        label.show()
        
        animacion = QPropertyAnimation(label, b"pos")
        animacion.setDuration(500)  
        animacion.setStartValue(punto_inicio)
        animacion.setEndValue(punto_destino)
        animacion.setEasingCurve(QEasingCurve.OutQuad)
        
        label.animacion = animacion 
        animacion.start()

    def agregar_carta_a_mano(self, mano, es_jugador, nombre_archivo):
        nuevo_label = QLabel(self)
        nuevo_label.setScaledContents(True)
        
        if es_jugador:
            nuevo_label.resize(self.lbl_carta.size())
        else:
            nuevo_label.resize(self.lbl_carta_dealer.size())
            
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        nuevo_label.setPixmap(QPixmap(os.path.join(ruta_actual, "Cards (large)", nombre_archivo)))
        
        desplazamiento = len(mano) * 30  
        
        if es_jugador:
            destino = QPoint(self.lbl_carta.x() + desplazamiento, self.lbl_carta.y())
        else:
            destino = QPoint(self.lbl_carta_dealer.x() + desplazamiento, self.lbl_carta_dealer.y())
            
        mano.append(nuevo_label)
        self.animar_carta(nuevo_label, destino)

    def sacar_carta_azar(self):
        palos = ["hearts", "diamonds", "clubs", "spades"]
        valores = list(self.valores_cartas.keys())
        palo = random.choice(palos)
        valor = random.choice(valores)
        return f"card_{palo}_{valor}.png", valor

    def iniciar_partida_global(self):
        self.lbl_tiempo.setText(f"Tiempo: {self.tiempo_restante}s")
        self.timer.start(1000)
        self.repartir_mesa()

    def repartir_mesa(self):
        nombre_archivo, valor = self.sacar_carta_azar()
        self.agregar_carta_a_mano(self.mano_dealer, es_jugador=False, nombre_archivo=nombre_archivo)
        
        self.puntaje_dealer += self.valores_cartas[valor]
        if valor == "A":
            self.ases_dealer += 1
            
        self.lbl_puntaje_dealer.setText(f"Dealer: {self.puntaje_dealer}")
        self.lbl_puntaje_jugador.setText("Tu Puntaje: 0")

    def pedir_carta(self):
        if self.juego_terminado or self.esperando_doble:
            return

        nombre_archivo, valor = self.sacar_carta_azar()
        self.agregar_carta_a_mano(self.mano_jugador, es_jugador=True, nombre_archivo=nombre_archivo)
        
        self.puntaje_jugador += self.valores_cartas[valor]
        if valor == "A":
            self.ases_jugador += 1
            
        while self.puntaje_jugador > 21 and self.ases_jugador > 0:
            self.puntaje_jugador -= 10
            self.ases_jugador -= 1
            
        self.lbl_puntaje_jugador.setText(f"Tu Puntaje: {self.puntaje_jugador}")
        
        if self.puntaje_jugador > 21:
            self.puntos_recompensa = 0
            self.estado_final = "Lose"
            self.lbl_tiempo.setText("¡TE PASASTE! (0 pts)")
            self.cerrar_juego_definitivo()

    def actualizar_reloj(self):
        if self.juego_terminado:
            return
            
        self.tiempo_restante -= 1
        
        if self.esperando_doble:
            self.lbl_tiempo.setText(f"¡Rápido! ({self.tiempo_restante}s) Ganaste 100 pts")
            if self.tiempo_restante <= 0:
                self.btn_doble.setVisible(False)
                self.esperando_doble = False
                self.lbl_tiempo.setText("¡Tiempo fuera! Te quedas con 100 pts.")
                self.puntos_recompensa = 100
                self.estado_final = "Win"
                self.cerrar_juego_definitivo()
            return

        self.lbl_tiempo.setText(f"Tiempo: {self.tiempo_restante}s")
        
        if self.tiempo_restante <= 0:
            self.lbl_tiempo.setText("¡TIEMPO AGOTADO!")
            self.plantarse()

    def plantarse(self):
        if self.juego_terminado or self.esperando_doble:
            return
            
        self.timer.stop()
        self.lbl_tiempo.setText("Turno del Dealer...")
        self.turno_dealer()

    def turno_dealer(self):
        while self.puntaje_dealer < 17:
            nombre_archivo, valor = self.sacar_carta_azar()
            self.agregar_carta_a_mano(self.mano_dealer, es_jugador=False, nombre_archivo=nombre_archivo)
            
            self.puntaje_dealer += self.valores_cartas[valor]
            if valor == "A":
                self.ases_dealer += 1
                
            while self.puntaje_dealer > 21 and self.ases_dealer > 0:
                self.puntaje_dealer -= 10
                self.ases_dealer -= 1
                
            self.lbl_puntaje_dealer.setText(f"Dealer: {self.puntaje_dealer}")
            
            loop = QEventLoop()
            QTimer.singleShot(700, loop.quit)
            loop.exec()
            
        self.determinar_ganador()

    def determinar_ganador(self):
        gano_mano = (self.puntaje_dealer > 21) or (self.puntaje_jugador > self.puntaje_dealer)
        empato_mano = (self.puntaje_dealer == self.puntaje_jugador)

        if self.en_doble_o_nada:
            if gano_mano:
                self.puntos_recompensa = 200
                self.estado_final = "Win"
                self.lbl_tiempo.setText("¡GANASTE EL DOBLE O NADA! (+200 pts)")
            elif empato_mano:
                self.puntos_recompensa = 50
                self.estado_final = "Win"
                self.lbl_tiempo.setText("¡EMPATE EN DOBLE O NADA! (+50 pts)")
            else:
                self.puntos_recompensa = 0
                self.estado_final = "Lose"
                self.lbl_tiempo.setText("PERDISTE EL DOBLE O NADA (0 pts)")
            
            # Si se le acabó el tiempo en el doble o nada, se marca TimeOut
            if self.tiempo_restante <= 0:
                 self.estado_final = "TimeOut"
                 
            self.cerrar_juego_definitivo()
            return

        if gano_mano:
            if self.tiempo_restante > 0:
                self.esperando_doble = True
                self.btn_doble.setVisible(True)
                self.lbl_tiempo.setText(f"¡GANASTE 100 PTS! ¿Doble o Nada? ({self.tiempo_restante}s)")
                self.timer.start(1000)  
            else:
                self.puntos_recompensa = 100
                self.estado_final = "Win"
                self.lbl_tiempo.setText("¡GANASTE! (+100 pts)")
                self.cerrar_juego_definitivo()
        elif empato_mano:
            self.puntos_recompensa = 50
            self.estado_final = "Win"
            self.lbl_tiempo.setText("¡EMPATE! (+50 pts)")
            if self.tiempo_restante <= 0:
                 self.estado_final = "TimeOut"
            self.cerrar_juego_definitivo()
        else:
            self.puntos_recompensa = 0
            self.estado_final = "Lose"
            self.lbl_tiempo.setText("EL DEALER GANA (0 pts)")
            if self.tiempo_restante <= 0:
                 self.estado_final = "TimeOut"
            self.cerrar_juego_definitivo()

    def jugar_doble_o_nada(self):
        if not self.esperando_doble or self.tiempo_restante <= 0:
            return
            
        self.btn_doble.setVisible(False)
        self.esperando_doble = False
        self.en_doble_o_nada = True  
        self.puntos_recompensa = 0   
        
        for carta in self.mano_jugador + self.mano_dealer:
            carta.deleteLater()
        self.mano_jugador.clear()
        self.mano_dealer.clear()
        
        self.puntaje_jugador = 0
        self.ases_jugador = 0
        self.puntaje_dealer = 0
        self.ases_dealer = 0
        
        self.lbl_tiempo.setText(f"¡DOBLE O NADA! Tiempo: {self.tiempo_restante}s")
        self.repartir_mesa()

    def cerrar_juego_definitivo(self):
        self.juego_terminado = True
        self.esperando_doble = False
        self.btn_doble.setVisible(False)
        self.timer.stop()
        
        # Pausamos 2 segundos para que el jugador alcance a leer si ganó o perdió
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        
        # En vez de usar sockets, cerramos la ventana. 
        # Esto le devuelve el control a la función jugar() de abajo.
        self.accept() 


def jugar():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    juego = JuegoBlackjack()
    juego.exec()
    
    # Retorno estandarizado
    return {
        "Result": juego.estado_final,
        "Score": juego.puntos_recompensa
    }

# Esto permite que sigas probando el juego haciendo "python minijuego_1.py" 
# sin necesidad de conectarte al servidor todavía.
if __name__ == "__main__":
    resultado, puntaje = jugar()
    print(f"--- PROTOCOLO HOST ---")
    print(f"Resultado a enviar: {resultado}")
    print(f"Puntaje a enviar: {puntaje}")