def abstract(func):
    '''
    Simulates the behaviour of abstract interface used in static typed languages (e.g. Java).
    '''
    def wrapper(*args, **kwargs):
        raise NotImplementedError()
    return wrapper
    
