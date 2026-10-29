import time
import random
from gpiozero import RotaryEncoder, Button

def play_game_2():
    # Inicializar pines del encoder (ajustar según tu conexión física)
    encoder = RotaryEncoder(a=5, b=6, max_steps=100)
    boton = Button(13)
    
    # Generar la operación matemática asegurando un resultado entre 0 y 100
    operacion = random.choice(['+', '-', '*'])
    if operacion == '+':
        a = random.randint(0, 100)
        b = random.randint(0, 100 - a)
        resultado_correcto = a + b
    elif operacion == '-':
        a = random.randint(0, 100)
        b = random.randint(0, a)
        resultado_correcto = a - b
    else:
        a = random.randint(0, 10)
        b = random.randint(0, 10)
        resultado_correcto = a * b
        
    tiempo_maximo = 15.0
    
    print(f"\n--- MINIJUEGO 2: RESOLVER CÓDIGO MATEMÁTICO ---")
    print(f"Resuelve la operación en menos de 15 segundos.")
    print(f"¿Cuánto es: {a} {operacion} {b}?")
    print("Gira el encoder para buscar tu respuesta y presiona el botón.")
    print("-----------------------------------------------")
    
    inicio = time.time()
    valor_anterior = None
    
    # Bucle principal restringido al tiempo máximo
    while (time.time() - inicio) < tiempo_maximo:
        # El encoder inicia asumiendo el valor 50 como centro
        valor_actual = encoder.steps + 50
        
        # Limitar visualmente el valor en pantalla entre 0 y 100
        valor_actual = max(0, min(100, valor_actual))
        
        # Imprimir solo cuando el jugador mueve la perilla
        if valor_actual != valor_anterior:
            print(f"Respuesta seleccionada: {valor_actual}")
            valor_anterior = valor_actual
            
        # Evaluar la respuesta al presionar el botón
        if boton.is_pressed:
            if valor_actual == resultado_correcto:
                print("\n¡Respuesta CORRECTA! Tarea completada.")
                encoder.close()
                boton.close()
                return {"Result": "Win", "Score": 100}
            else:
                print(f"\n¡Respuesta INCORRECTA! Fallaste. El resultado era {resultado_correcto}.")
                encoder.close()
                boton.close()
                return {"Result": "Lose", "Score": 0}
                
        time.sleep(0.1) # Pausa para estabilidad del procesador
        
    # Condición de TimeOut si se agotan los 15 segundos
    print(f"\n¡Se acabó el tiempo! El resultado correcto era {resultado_correcto}.")
    
    valor_final = max(0, min(100, encoder.steps + 50))
    distancia = abs(resultado_correcto - valor_final)
    
    # Puntaje proporcional según la cercanía a la respuesta correcta
    score_timeout = max(1, 99 - distancia)
    
    # Liberar recursos de hardware
    encoder.close()
    boton.close()
    
    return {"Result": "TimeOut", "Score": score_timeout}

# Prueba local independiente
if __name__ == "__main__":
    game_id = 2
    resultado = play_game_2()
    print(f"GameID={game_id} | Result y Score obtenidos: {resultado}")