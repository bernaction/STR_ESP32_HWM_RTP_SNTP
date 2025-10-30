# tcp_keys_client.py — Windows (usa msvcrt.getch)
import socket, time, msvcrt
from datetime import datetime


#ESP_IP = "172.20.10.10"   # coloque o IP da sua ESP32
ESP_IP = "192.168.100.185"
PORT   = 5000

def now_ms(): return int(time.time()*1000)

def recv_line(sock, timeout=0.5):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk: break
            data += chunk
            if b"\n" in chunk: break
    except Exception:
        pass
    return data.decode(errors="ignore").strip()

def main():
    with socket.create_connection((ESP_IP, PORT), timeout=5) as s:
        # mensagem de boas-vindas (se houver)
        try:
            print(recv_line(s, timeout=1.0))
        except Exception:
            pass

        print("\nControles: [1]=SORT  [2]=SAFE  [3]=SET 3000  [4]=ping  [q]=sair\n")
        while True:
            ch = msvcrt.getch()
            if not ch: 
                continue
            key = ch.decode('ascii', errors='ignore').lower()
            if key == 'q':
                print("Saindo…")
                break
            if key == '1':
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                print(f"{timestamp} > 1 apertado")
                msg = "SORT"
            elif key == '2':
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                print(f"{timestamp} > 2 apertado")
                msg = "SAFE"
            elif key == '3':
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                print(f"{timestamp} > 3 apertado")
                msg = "SET 3000"
            elif key == '4':
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                print(f"{timestamp} > 4 apertado")
                msg = "ping"
            else:
                continue  # ignora outras teclas

            t0 = now_ms()
            s.sendall((msg + "\n").encode())
            resp = recv_line(s, timeout=0.5)
            rtt = now_ms() - t0
            # prepare human-friendly response text: show explicit marker when no data
            if resp:
                resp_text = resp
            else:
                resp_text = "<NO RESPONSE>"  # indicates timeout/closed connection
            # timestamp with milliseconds: DD/MM/YYYY HH:MM:SS.mmm
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
            print(f"{timestamp} > {msg} | ESP respondeu: {resp_text}  [tcp_rtt_ms={rtt}]")
if __name__ == "__main__":
    main()
