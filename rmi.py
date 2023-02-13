from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
import message
from synchronized import synchronized
import socket
import inspect
import traceback
import dill
import logging

class Remote():
    '''
    Marker class
    '''
    def __init__(self):
        super().__init__()


class RemoteObject(Remote):
    stubs = dict()
    def __init__(self):
        super().__init__()

        
    @staticmethod
    @synchronized
    def addStub(obj, stub):
        RemoteObject.stubs[obj] = stub

    
    @staticmethod
    @synchronized
    def deleteStub(obj):
        RemoteObject.stubs.pop(obj)



    @staticmethod
    @synchronized
    def toStub(obj):
        if RemoteObject.stubs.get(obj):
            return RemoteObject.stubs.get(obj)
        else:
            raise Exception('no such object exist')


class RMISocketFactory:
    '''
    An RMISocketFactory instance is used by the RMI runtime in order to obtain client and server sockets for RMI calls. An application may use the setSocketFactory method to request that the RMI runtime use its socket factory instance instead of the default implementation.
    You can use the RMISocketFactory class to create a server socket that is bound to a specific address, restricting the origin of requests. For example, the following code implements a socket factory that binds server sockets to an IPv4 loopback address. This restricts RMI to processing requests only from the local host.

    # https://docs.oracle.com/javase/8/docs/api/java/rmi/server/RMISocketFactory.html
    '''
    def create_server_socket(self, port=0):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.listen()
        logging.info('server socket created at', sock.getsockname())
        host = socket.gethostbyname(socket.gethostname())
        port = sock.getsockname()[1]
        endpoint = f'{host}:{port}'
        return sock, endpoint

    def create_client_socket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock



class UnicastRemoteObject():
    '''
    Used for exporting a remote object and obtaining a stub that communicates to the remote object. Stubs are either generated at runtime using dynamic proxy objects, or they are generated statically at build time.

    # https://docs.oracle.com/javase/8/docs/api/java/rmi/server/UnicastRemoteObject.html
    '''
    def __init__(self):
        super().__init__()
        

    @staticmethod
    def export_object(remote_object, port=0, socket_factory=RMISocketFactory()):
        '''
        Exports the remote object to make it available to receive incoming calls, using a transport specified by the given socket factory.
        '''
        ref = UnicastServerRef(port, socket_factory, remote_object)
        ref.init_server()
        proxy = ref.export_object()
        return proxy

class Registry:
    '''
    Registry is a remote interface to a simple remote object registry that provides methods for storing and retrieving remote object references bound with arbitrary string names.
    '''
    _protocol = 'tcp'
    _clients = []

    def __init__(self, port=1099):
        super().__init__()
        self.remote_objects = {}


    def bind(self, obj, name):
        if (self.remote_objects.get(name)):
            raise Exception(f'{name} is already bound')
        else:
            self.remote_objects[name] = obj


    def unbind(self, name):
        if(self.remote_objects.get(name)):
            self.remote_objects.pop(name)
        else:
            raise Exception(f'{name} is not currently bound')

    def rebind(self, obj, name):
        self.remote_objects[name] = obj
        

    def list(self):
        return list(self.remote_objects.keys())


    def lookup(self, name) -> Remote:
        if(self.remote_objects.get(name)):
            obj = self.remote_objects.get(name)
            return obj
        else:
            raise Exception(f'{name} is not currently bound')


class LocateRegistry:
    '''
    LocateRegistry is used to obtain a reference to a bootstrap remote object registry on server, or to create a remote object registry that accepts calls on a specific port.
    Note that a getRegistry call does not actually make a connection to the remote host. It simply creates a local reference to the remote registry and will succeed even if no registry is running on the remote host. Therefore, a subsequent method invocation to a remote registry returned as a result of this method may fail.

    # https://docs.oracle.com/javase/8/docs/api/java/rmi/registry/LocateRegistry.html
    '''
    _port = 1099
    def __init__(self):
        super().__init__()


    @staticmethod
    def create_registry(port) -> Registry:
        '''
        LocateRegistry is used to obtain a reference to a bootstrap remote object registry on a particular host (including the local host), or to create a remote object registry that accepts calls on a specific port.
        '''
        registry = Registry(port)
        ref = UnicastServerRef(port, RMISocketFactory(), registry)
        ref.init_server()
        proxy = ref.export_object()
        return proxy
        

    @staticmethod
    def get_registry(host, port) -> Registry:
        '''
        Returns a reference to the the remote object Registry for the local host on the specified port.
        '''
        ref = UnicastServerRef(port, RMISocketFactory(), Registry())
        ref.set_ep(host, port)
        proxy = ref.export_object()
        return proxy



class UnicastServerRef:
    '''
    UnicastServerRef implements the remote reference layer server-side behavior for remote objects.
    '''
    __futures = []
    def __init__(self, port: int, socket_factory: RMISocketFactory, remote_object: Remote):
        super().__init__()
        self.__executor = ThreadPoolExecutor(max_workers=32)
        self.__ep = f'localhost:{port}'
        self.server_sock = None
        self.remote_object = remote_object
        self.__port = port
        self.socket_factory = socket_factory
        
        
    def init_server(self):
        self.server_sock, self.__ep = self.socket_factory.create_server_socket(self.__port)
        Thread(target=self.start_server_socket).start()

    def set_ep(self, host: str, port: str|int):
        self.__ep = f'{host}:{port}'
        self.__port = port


    def start_server_socket(self):
        '''
        Starts server and binds to accept incoming connections. All incoming connections are handled in
        a thread pool when new connection accepted.
        '''
        while True:
            conn, addr = self.server_sock.accept()
            t = self.__executor.submit(fn=self.new_conn, conn=conn, addr=addr)
            # self.__futures.append(t)
            # for future in as_completed(self.__futures):
            #     try:
            #         print("thread finished, result is ",future.result())
            #     except TimeoutError():
            #         print("ConnectTimeout.")
            # print(len(self.__futures))


    def new_conn(self, conn: socket, addr: socket._RetAddress):
        '''
        Handles data communication and method calls from client until message data arguments fully received
        and method run processed its implementation to prepare return value. Sends back return value as binary
        serialization to caller.
        '''
        logging.debug(conn, addr)
        with conn:
            logging.debug('Connected by', addr)
            data = conn.recv(2048)
            msg = dill.loads(data)
            if isinstance(msg, message.InvokeMessage):
                try:
                    res = self._run_(msg.method, msg.args)
                    conn.sendall(dill.dumps(res))
                except Exception as e:
                    logging.exception('exception:', e)
                    traceback.print_exc()
        return

    def _run_(self, method_name, args):
        '''
        Finds method by its name in a remote accessible object and executes it.
        :param method_name: name of the method in object
        :param args: arguments to pass into method_name
        :return: value from original return statement of method_name in remote object
        '''
        method = getattr(self.remote_object, method_name)
        return method(*args)


    def export_object(self):
        proxy = Proxy(self.__ep, self.remote_object)
        return proxy



class Proxy(Remote):
    def __init__(self, ep, obj_interface, socket_factory=RMISocketFactory()):
        self.ep = ep
        unallowed = ['_invoke_', 'ep', '_create_method_']
        self.socket_factory = socket_factory
        methods = filter(lambda x: x not in unallowed ,get_method_names(obj_interface))
        for m_name in methods:
            method = self._create_method_(self._invoke_, m_name)
            setattr(self, m_name, method)


    def _invoke_(self, method, args):
        host = self.ep.split(':')[0]
        port = int(self.ep.split(':')[1])
        with self.socket_factory.create_client_socket(host, port) as client_sock:
            msg = message.InvokeMessage(method=method, args=args)
            client_sock.sendall(dill.dumps(msg))
            data = client_sock.recv(2048)
            if data:
                obj = dill.loads(data)
                return obj

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        
        return state


    def _create_method_(self, to_call, m_name):
        return lambda *args: to_call(m_name, args)



def get_methods(obj):
    '''
    Get python methods from a python runtime object.
    :param obj: python object
    :return: list of all methods in an object 
    '''
    methods = [member for member in [getattr(obj, attr) for attr in dir(obj)] if inspect.ismethod(member)]
    return methods

def get_method_names(obj):
    '''
    Get method names from a python runtime object.
    :param obj: python object
    :return: list of all method names in an object 
    '''
    method_names = [attr for attr in dir(obj) if (inspect.ismethod(getattr(obj, attr)) and not attr.startswith('__'))]
    return method_names

