class SendLKException(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, status: str = "ERROR", message: str = "") -> None:
        super().__init__(self, message)
        self._status = status
        self._message = message
        
    @property
    def status(self):
        return self._status
    
    @property
    def message(self):
        return self._message
    
    def __str__(self):
        return f'{self.status} : {self.message}'