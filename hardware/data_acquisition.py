import serial
import serial.tools.list_ports
import time
import os

# Configurações
BAUD_RATE = 9600  # Velocidade padrão (ajuste se o hardware for diferente)
FILE_NAME = '../../data.txt'

def find_usb_port():
    """Tenta encontrar automaticamente a porta onde o hardware está plugado"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(f"Detectada: {p.device}")
        return p.device
    return None

def start_acquisition():
    port = find_usb_port()
    if not port:
        print("❌ Nenhum hardware USB detectado! Verifique o cabo.")
        return

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        print(f"✅ Conectado em {port}. Gravando dados... (Ctrl+C para parar)")
        
        # Limpa o arquivo anterior para começar um teste novo
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)

        start_time = time.time()

        while True:
            if ser.in_waiting > 0:
                # Lê a linha vinda do USB
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    curr_t = time.time() - start_time
                    # Salva no formato que o sistema aceita
                    with open(FILE_NAME, 'a') as f:
                        f.write(f"{curr_t:.4f}\t{line}\n".replace('.', ','))
                        
    except KeyboardInterrupt:
        print("\n⏹️ Aquisição encerrada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'ser' in locals(): ser.close()

if __name__ == "__main__":
    start_acquisition()