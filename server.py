import socket
import random
from datetime import datetime
import struct
server_ip = '127.0.0.1'
server_port = 23333
loss = 30  # 模拟丢包

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))
    print(f"服务器正在运行在 {server_ip}:{server_port}")

    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            if len(data)<200: # 少于200证明收到的是模拟三次握手和四次挥手报文
                message = data.decode()
                if message == "SYN":
                    print(f"收到来自 {client_address} 的 SYN")
                    server_socket.sendto("SYN-ACK".encode(), client_address)
                    continue
                elif message == "CONNECT-ACK":
                    print(f"与 {client_address} 建立连接")
                    continue
                elif message == "FIN":
                    print(f"收到来自 {client_address} 的 FIN")
                    server_socket.sendto("FIN-ACK".encode(), client_address)
                    continue
                elif message == "RELEASE-ACK":
                    print(f"与 {client_address} 释放连接")
                    continue
            else:
                seq_no, ver, content =  struct.unpack('!HB200s',data) # 解包
                seq_no = int(seq_no)
                ver = int(ver)
                print(f"收到来自 {client_address} 的第{seq_no}号报文:{content} ")
            # 模拟丢包
                if random.uniform(1,100) < loss:
                    print(f"丢弃报文 {seq_no}")
                    continue
                content = datetime.now().strftime('%H-%M-%S')#记录时间
                message = struct.pack('!HB200s', seq_no, ver, content.ljust(200, 'a').encode()) # 打包
                server_socket.sendto(message, client_address)
                print(f"发送响应报文 {seq_no} 给 {client_address}")

        except Exception as e:
            print(f"错误: {e}")
    server_socket.close()
if __name__ == "__main__":
    main()
