class BaseResponse:
    def __init__(self, status: str = "SUCCESS", message: str = "") -> None:
        self._status = status
        self._message = message
    
    @property
    def status(self):
        return self._status
    
    @property
    def message(self):
        return self._message

    def __str__(self):
        return f'{self._status} : {self._message}'

class SmsResponse(BaseResponse):
    def __init__(self, status: str = "SUCCESS", message: str = "", data: dict = None):
        if data is None:
            data = {}
        super().__init__(status, message)
        self._uid = data.get('uid')
        self._receiver = data.get('to')
        self._sender = data.get('from')
        self._text = data.get('message')
        self._text_status = data.get('status')
        self._cost = data.get('cost')
        self._data = {}
        
    @property
    def uid(self):
        return self._uid

    @property
    def receiver(self):
        return self._receiver

    @property
    def sender(self):
        return self._sender

    @property
    def text(self):
        return self._text

    @property
    def delivery_status(self):
        return self._text_status

    @property
    def cost(self):
        return self._cost
    
    @property
    def data(self):
        return self._data
    
    def add_data(self, key: str, value: str):
        self._data[key] = value

class ProfileResponse(BaseResponse):
    def __init__(self, status: str = "SUCCESS", message: str = "", data: dict = None):
        if data is None:
            data = {}
        super().__init__(status, message)
        self._used_unit = data.get('used_unit')
        self._remaining_unit = data.get('remaining_unit')
        self._expired_on = data.get('expired_on')
        
    @property
    def used(self) -> int:
        try:
            return int(self._used_unit)
        except (ValueError, TypeError):
            return 0
    
    @property
    def remaining(self) -> int:
        try:
            return int(self._remaining_unit)
        except (ValueError, TypeError):
            return 0
    
    @property
    def expired_on(self):
        return self._expired_on
