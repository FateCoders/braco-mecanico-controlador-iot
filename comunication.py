# comunication.py
import serial
import time

# A variável de conexão vive aqui
arduino = None

def conectar_arduino(porta_com, baud_rate=9600):
    """Tenta conectar ao Arduino na porta especificada."""
    global arduino
    if arduino and arduino.is_open:
        desconectar_arduino()
        
    try:
        arduino = serial.Serial(porta_com, baud_rate, timeout=1)
        time.sleep(2) # Espera a conexão estabilizar
        
        resposta_arduino = ""
        if arduino.in_waiting > 0:
            resposta_arduino = arduino.readline().decode().strip()
            print(f"[Arduino]: {resposta_arduino}")
            
        print(f"Conexão {porta_com} estabelecida.")
        return True, f"Conectado em {porta_com}", resposta_arduino
        
    except Exception as e:
        arduino = None
        print(f"Erro ao conectar: {e}")
        return False, f"Falha ao conectar em {porta_com}", str(e)

def desconectar_arduino():
    """Fecha a conexão serial se estiver aberta."""
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        print("Conexão serial fechada.")
    arduino = None

def enviar_comando(motor, direcao, passos, delay):
    """Envia um comando formatado para o Arduino, se conectado."""
    global arduino
    if arduino is None or not arduino.is_open:
        print("Erro: Arduino não está conectado.")
        return False, "Arduino não conectado"
        
    try:
        cmd = f"{motor},{direcao},{passos},{delay}\n"
        arduino.write(cmd.encode())
        time.sleep(0.05) # Pequena pausa para o Arduino processar
        
        resposta = ""
        while arduino.in_waiting > 0:
            resposta = arduino.readline().decode().strip()
            print(f"[Arduino]: {resposta}")
        
        return True, resposta
        
    except Exception as e:
        print(f"Erro na comunicação serial: {e}")
        desconectar_arduino() # Fecha a conexão se algo der errado
        return False, f"Erro serial: {e}"