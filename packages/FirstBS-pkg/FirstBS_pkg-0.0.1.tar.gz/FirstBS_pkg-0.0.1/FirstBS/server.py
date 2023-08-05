# server에서 client를 통제하는 프로그램
# client의 접속을 통제하고, 입력값을 그대로 받아와 server에서 출력해내는 프로그램
# delay_server.py
# 초기 구문은 memo에서 가져오면 됨


import socket
import threading
import psutil
from pynput.keyboard import Key, Listener
from FirstBS import module_conclient


def Client():
    module_conclient.Conclient()
    # 상대경로
    #os.system(os.getcwd()+"/module_conclient.py")
    # 절대경로
    #os.system("C:/Users/qudtnwkdrns1_estsecu/Desktop/Python/control_client.py") 

# f10 입력까지는 올바르게 작동함,
# f10 입력받으면 클라이언트를 죽이는 과정만 완료하면 문제 없을 거 같은데


def Started(key):       # f10이 입력되면 아래 if문 실행, else라면 아무 일 없이 함수 종료하도록 return
    pid = psutil.Process()        # 해당 프로세스의 ppid를 변수에 저장하는 구문

    if key == Key.f10:
        print("**Terminated the Client.**")
        #threading.Condition(wait())
        #play_Listen.join()
        pid.terminate()
        
        # while True:     # 클라이언트 종료 이후 서버유지의 유무를 선택하는 구문
        #     server_end = input("서버를 종료하시겠습니까? (Y/N)")
        #     if server_end == "Y":
        #         print("서버 종료")
        #         exit()
        #     elif server_end == "N":
        #         print("서버는 실행")
        #         break
        #     else:
        #         print("잘못된 입력값입니다.")
    else:
        return # 다른 입력값이면 함수를 종료하도록 return 


def Listen():          # 멀티 스레드로 키보드 입력을 감지하고 있음
    with Listener(on_press=Started) as listener:
        listener.join()


def Conserver():
    print("서버가 개설되었습니다.")

    server = socket.socket()
    server.bind(('0.0.0.0', 6543))
    # bind 한다 = 어떠한 네트워크에서 대기 할 것인지 정한다.
    # 첫 번째 인자, 127.0.0.1 내 컴퓨터의 랜 / 0.0.0.0 모든 랜
    # 몇 번 port에서 기다릴지도 정해줘야 한다.

    server.listen() # 기다리겠다 !

    play_client = threading.Thread(target = Client)     # Client 함수를 스레드로 호출
    play_client.daemon = True       # 데몬 스레드로 정의함으로써, 종료 이후의 불필요한 cpu 사용을 방지
    play_client.start()    



    play_Listen = threading.Thread(target = Listen)     # Listen 함수를 스레드로 호출
    play_Listen.daemon = True       # 데몬 스레드로 정의함으로써, 종료 이후의 불필요한 cpu 사용을 방지
    play_Listen.start()


    conn, addr = server.accept() # 클라이언트가 붙을 때 까지 기다리겠다. 두 개의 결과값을 제공
    #     # conn 클라이언트의 객체, addr 클라이언트 객체의 주소


    while True:
        data = conn.recv(1024) # 클라이언트가 보낸 걸 얼마만큼 읽을 것인지 정해주는 구간
            # 1024바이트 만큼 읽을 것이라고 함, 그 내용을 data에 담는다.
        print(data)