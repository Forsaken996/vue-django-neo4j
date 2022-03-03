import threading
from time import sleep

def prin(i):
    print(i)
    sleep(1)
    print(i*10)

t1 = threading.Thread(target=prin, args=(1,))
t2 = threading.Thread(target=prin, args=(2,))
t2.start()
t1.start()