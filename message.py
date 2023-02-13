class InvokeMessage(object):
    '''
    Invoke message type in communication from client to server.
    Client calls encapsulates the method call and passed arguments to it as binary python object
    created from InvokeMessage class. 
    '''
    def __init__(self, **kwargs):
        super().__init__()
        self.method = kwargs.get('method')
        self.args = kwargs.get('args')


