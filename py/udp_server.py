# udp_server.py — PC (ajustado p/ compatibilidade com ESP)
import socket, time, json
from datetime import datetime

ADDR = ("0.0.0.0", 6010)
def now_us(): return int(time.time() * 1_000_000)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(ADDR)
print("Aguardando UDP em", ADDR, "…")

while True:
    data, src = s.recvfrom(2048)
    t_pc_recv = now_us()
    txt = data.decode(errors="ignore").strip()
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
    print(f"{timestamp} <- {src} => {txt}  [t_pc_recv_us={t_pc_recv}, size={len(data)}]")

    # Eco p/ ESP medir RTT e (futuramente) one-way delay
    reply = json.dumps({
        "proto": "UDP",
        "t_pc_recv_us": t_pc_recv,
        "t_pc_send_us": now_us(),
        "size": len(data),
        "echo": txt
    })
    s.sendto(reply.encode(), src)