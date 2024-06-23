import argparse
import socket
import time
import struct
# 定义请求报文总数和版本号
total_requests = 12
version = 2
def parse_arguments():
    parser = argparse.ArgumentParser(description="发送UDP报文到指定服务器")
    parser.add_argument("--server_ip", type=str, default="127.0.0.1",help="服务器IP地址")
    parser.add_argument("--server_port", type=int, default=23333,  help="服务器端口号")
    return parser.parse_args()
def main(server_ip, server_port):
    timeout = 0.1  # 超时时间
    max_retransmissions = 2  # 最大重传次数

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    seq_no = 1  # 报文序列号初始化为1
    received_packets = 0  # 接收到的报文数
    rtt_list = []

    print(f"正在连接到服务器 {server_ip}:{server_port}...")

    try:
        # TCP的三次握手
        client_socket.sendto("SYN".encode(), (server_ip, server_port))
        try:
            data, _ = client_socket.recvfrom(1024)
            if data.decode() == "SYN-ACK":
                print("成功收到SYN-ACK包")
                client_socket.sendto("CONNECT-ACK".encode(), (server_ip, server_port))
                print("连接建立成功。")
            else:
                print("连接建立失败。")
                return
        except socket.timeout:
            print("连接超时。")
            return

        first_time = last_time = None # 用来计算总响应时间

        for _ in range(total_requests):
            content = "221002304lmzadfwsfFSwfgWFDeeggWFDFAGGFAGGw"
            message = struct.pack('!HB200s',seq_no,version,content.ljust(200,'a').encode())
            for i in range(max_retransmissions):  # 重传
                try:
                    start_time = time.time()  # 记录发送时间
                    client_socket.sendto(message, (server_ip, server_port))
                    data_server,_ = client_socket.recvfrom(1024)  # 等待响应
                    response_seq_no, response_ver, server_content = struct.unpack('!HB200s',data_server) # 解包
                    response_seq_no = int(response_seq_no)
                    response_ver = int(response_ver)

                    if response_seq_no == seq_no and response_ver == version:
                        rtt = (time.time() - start_time) * 1000
                        rtt_list.append(rtt)
                        print(f"sequence no: {seq_no}, rtt: {rtt:.2f} 毫秒, content: {server_content}")
                        if first_time is None:
                            first_time = time.time()
                        received_packets += 1
                        break
                except socket.timeout:
                    print(f"序列号: {seq_no}, 请求超时。")
                    if i == max_retransmissions - 1:
                        print("达到最大重传次数,放弃重传")

            seq_no += 1

        # TCP四次挥手
        client_socket.sendto("FIN".encode(), (server_ip, server_port))
        try:
            data, _ = client_socket.recvfrom(1024)
            if data.decode() == "FIN-ACK":
                client_socket.sendto("RELEASE-ACK".encode(), (server_ip, server_port))
                print("连接已释放。")
                last_time = time.time()
        except socket.timeout:
            print("释放连接时超时。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        client_socket.close()

    # 汇总信息

    total_lost = total_requests - received_packets
    loss_rate = (total_lost / total_requests) * 100
    if rtt_list:
        max_rtt = max(rtt_list)
        min_rtt = min(rtt_list)
        avg_rtt = sum(rtt_list) / len(rtt_list)
        stddev_rtt = (sum((rtt - avg_rtt) ** 2 for rtt in rtt_list) / len(rtt_list)) ** 0.5
        overall_time = last_time - first_time if first_time and last_time else 0
        print(f"接收到的报文总数: {received_packets}")
        print(f"丢包率: {loss_rate:.2f}%")
        print(f"max_RTT: {max_rtt:.2f} 毫秒")
        print(f"min_RTT: {min_rtt:.2f} 毫秒")
        print(f"avg_RTT: {avg_rtt:.2f} 毫秒")
        print(f"stddev_RTT: {stddev_rtt:.2f} 毫秒")
        print(f"服务器总响应时间: {overall_time:.2f} 秒")

if __name__ == "__main__":

    args = parse_arguments()
    server_ip = args.server_ip
    server_port = args.server_port
    main(args.server_ip, args.server_port)