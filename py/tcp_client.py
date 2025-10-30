# tcp_keys_client.py — Windows (usa msvcrt.getch)
import socket, time, msvcrt, json
from datetime import datetime

ESP_IP = "172.20.10.10"   # IP da sua ESP32
PORT   = 5000

def now_ms(): return int(time.time() * 1000)
def now_us(): return int(time.time() * 1_000_000)

def recv_line(sock, timeout=0.5):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"\n" in chunk:
                break
    except Exception:
        pass
    return data.decode(errors="ignore").strip()

def main():
    with socket.create_connection((ESP_IP, PORT), timeout=5) as s:
        # banner opcional
        try:
            print(recv_line(s, timeout=1.0))
        except Exception:
            pass

        print("\nControles: [1]=SORT  [2]=SAFE  [3]=SET 3000  [4]=PING  [q]=sair\n")
        seq = 0

        while True:
            ch = msvcrt.getch()
            if not ch:
                continue
            key = ch.decode('ascii', errors='ignore').lower()
            if key == 'q':
                print("Saindo…")
                break

            # comandos “simples” (sem medição de one-way)
            if key in ('1', '2', '3'):
                if key == '1':
                    msg = "SORT"
                elif key == '2':
                    msg = "SAFE"
                else:
                    msg = "SET 3000"

                t0 = now_ms()
                s.sendall((msg + "\n").encode())
                resp = recv_line(s, timeout=0.5)
                rtt = now_ms() - t0

                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                print(f"{timestamp} > {msg} | ESP respondeu: {resp or '<NO RESPONSE>'}  [tcp_rtt_ms={rtt}]")
                continue

            # comando PING com timestamps em microssegundos
            if key == '4':
                t_pc_send = now_us()
                ping_payload = f'PING {{"seq":{seq},"t_pc_send_us":{t_pc_send}}}\n'
                s.sendall(ping_payload.encode())

                resp = recv_line(s, timeout=0.8)
                t_pc_recv = now_us()

                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

                if not resp:
                    print(f"{timestamp} > PING seq={seq} | <NO RESPONSE>")
                    seq += 1
                    continue

                # tenta decodificar JSON do servidor
                try:
                    j = json.loads(resp)
                    # RTT (robusto, independe de offset SNTP)
                    rtt_us = t_pc_recv - t_pc_send
                    # one-way (estimativa, depende de SNTP ok nos dois lados)
                    owd_pc2esp = j.get("t_esp_recv_us", 0) - j.get("t_pc_send_us", 0)
                    owd_esp2pc = t_pc_recv - j.get("t_esp_send_us", 0)

                    print(
                        f"{timestamp} > PING seq={seq} | "
                        f"RTT={rtt_us}us  "
                        f"pc->esp≈{owd_pc2esp}us  "
                        f"esp->pc≈{owd_esp2pc}us  "
                        f"resp={j}"
                    )
                except Exception as e:
                    # servidor pode responder outra coisa (ex.: banner), apenas exibe
                    print(f"{timestamp} > PING seq={seq} | resp='{resp}' (não-JSON)")

                seq += 1
                continue

            # ignora outras teclas
            continue

if __name__ == "__main__":
    main()
