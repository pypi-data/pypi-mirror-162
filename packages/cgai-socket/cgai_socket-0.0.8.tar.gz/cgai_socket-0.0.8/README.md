# cgai-socket

#### 介绍
简单轻量又快速的socket服务与客户请求库，支持绑定自定义函数

#### 安装
```cmd
pip install cgai-socket
```

#### 使用说明

server:
```python
from cgai_socket.cgai_server import Server


def func1(data):
    print('func1',data)
    return None

def func2(data,_id,_name):
    print('func2:',_id,_name)
    return None

def func3(data,_id2,_name2):
    print('func2:',_id2,_name2)
    return 'func2'

HOST = '192.168.53.3'
PORT = 24601
BUFFER = 20480

call_backs = {func1:None,func2:(1,'CGAI01'),func3:(2,'CGAI02')}

server = Server(HOST,PORT,BUFFER,call_backs=call_backs)
server.listening()
```

client:
```python

from cgai_socket.cgai_client import Client


HOST = '192.168.53.3'
PORT = 24601
BUFFER = 20480

my_client = Client(HOST,PORT,BUFFER)

msg = {'a':1,'b':2,'c':3}

result = my_client.send(msg)
print('result:',result)
```


#### 回调函数的定义

关于回调函数的定义格式：  

    回调函数的目的就是与客户端传来的数据进行交互，因此在自定义回调函数时:
    1.必须有占位形参data(名称可随意改)。
    2.每个回调函数必须有一个返回值，该可以为空，当不为空时，成功执行回调函数后会将该值传回给客户端，实现即时通信的效果

回调函数定义格式如下为：  

    >>> def func(data,*args):
    >>>     xxxx
    >>>     return None
其中data为占位形参，你可以直接把它当做已知的从客户端传送过来的数据来直接操作。  
假如我们知道从客户端传送的数据是{"a":1,"b":2}，那么我们可以如此创建回调函数来使用数据：  

    >>> def myfunc(data,_id,_name):
    >>>     if data:
    >>>         print("my data : ",data)
    >>>         print("a : ",data.get('a',None))
    >>>         print("_id : ",_id)
    >>>         print("_name : ",_name)
    >>>         return None

#### 添加回调函数

1.使用add_callback添加回调函数：

    使用add_callback添加回调函数时可以传入参数，但是不需要传入data。因为data是客户端传来的数据，
    这里只是当中占位参数。例：
    >>> from cgai_socket.cgai_server import Server
    >>>
    >>> def myfunc(data,_id,_name):
    >>>     print(data.get('a',''))
    >>>     print(_id,_name)
    >>>     return None
    >>>
    >>> my_server = Server('192.168.1.88',24601,1024)
    >>> my_id = 12
    >>> my_name = 'CGAI'
    >>> my_server.add_callback(myfunc,args=(my_id,my_name))
    >>> my_server.listening()

    如果还有其他回调函数需要添加，可以继续使用add_callback,比如：
    >>> def func1(data):xxx return None
    >>> def func2(data):xxx return None
    >>> ...
    >>> my_server.add_callback(func1)
    >>> my_server.add_callback(func2)
    >>> ...

注意：只有当所有回调函数添加完成后，最后执行listening开启服务。


初始化创建server时添加多个回调函数:  

    在初始化server时，是可以直接一次性添加多个回调函数，使用关键字参数 call_backs,
    call_backs是一个字典，它使用结构是:
    >>> {func1_name:(func1_args),func2_name:(func2_args),...}

    例：
    >>> def func1(data):xxx return None
    >>> def func2(data,_id,_name):xxx return None
    >>> def func3(data,_id1,_name2):xxx return None
    >>> call_backs = {func1:None,func2:(_id,_name),fun3:(_id1,_name2)}
    >>> my_server = Server('192.168.1.88',24601,1024,call_backs=call_backs)


#### 后台运行server
    cgai-socket 支持使用threading模块实现后台运行服务
```python
import threading
import time
from cgai_socket.cgai_server import Server

def func1(data):
    print('func1',data)
    return '收到'


HOST = '192.168.53.3'
PORT = 24602
BUFFER = 20480

call_backs = {func1:None}


def init_server():
    server = Server(HOST,PORT,BUFFER,call_backs=call_backs)
    server.listening()


if __name__ == '__main__':
    start_time = time.time()
    t = threading.Thread(None, init_server)
    t.setDaemon(True)
    t.start()
    while True:
        end_time = time.time()
        if end_time - start_time > 10:
            print('停止主程序')
            break
```





#### 交流方式


wx: zxzxde


