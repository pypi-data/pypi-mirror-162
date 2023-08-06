import requests
from requests.sessions import PreparedRequest, Request
from sendlk import _app

App = _app.App.get_instance()

DEFAULT_TIMEOUT_SECONDS = 120

class HttpClient:
    
    __instance = None
    
    def __init__(self) -> None:
        """
        Initialize the HttpClient.
        Arguments:
            host {str} -- The host url to user for all the requests.
            timeout {int} -- The timeout to use for all the requests.
        Raises:
            ValueError: If host is None.
        """
        if HttpClient.__instance is not None:
            raise ValueError("HttpClient is a singleton class. Use get_instance() to get the instance.")
        self.host = App.url
        self.timeout = DEFAULT_TIMEOUT_SECONDS
        self.session = requests.Session()
        self.session.headers.update(App.get_headers())
        self.session.verify = True
        HttpClient.__instance = self

    @staticmethod
    def get_instance():
        """
        Get the instance of the HttpClient.
        Returns:
            HttpClient: The instance. 
        """
        return HttpClient() if HttpClient.__instance is None else HttpClient.__instance
    
    @staticmethod
    def get(path: str, params: dict = None) -> requests.Response:
        """
        Get a GET request.
        Arguments:
            path {str} -- The path to use.
            params {dict} -- The params to use.
        Returns:
            requests.Response -- The response.
        """
        request: Request = Request('GET', HttpClient.__instance.host + path, params=params)
        prepare_request: PreparedRequest = HttpClient.__instance.session.prepare_request(request)
        return HttpClient.__instance.session.send(prepare_request, timeout=HttpClient.__instance.timeout)
        

    @staticmethod
    def post(path: str, params: dict = None, data: dict = None) -> requests.Response:
        """
        Get a POST request.
        Arguments:
            path {str} -- The path to use.
            params {dict} -- The params to use.
            data {dict} -- The data to use.
        Returns:
            requests.Response -- The response.
        """
        request = Request('POST', HttpClient.__instance.host + path, params=params, json=data)
        prepare_request: PreparedRequest = HttpClient.__instance.session.prepare_request(request)
        return HttpClient.__instance.session.send(prepare_request, timeout=HttpClient.__instance.timeout)

    @staticmethod
    def put(path: str, params: dict = None, data: dict = None) -> requests.Response:
        """
        Get a PUT request.
        Arguments:
            path {str} -- The path to use.
            params {dict} -- The params to use.
            data {dict} -- The data to use.
        Returns:
            requests.Response -- The response.
        """
        request = Request('PUT', HttpClient.__instance.host + path, params=params, json=data)
        prepare_request: PreparedRequest = HttpClient.__instance.session.prepare_request(request)
        return HttpClient.__instance.session.send(prepare_request, timeout=HttpClient.__instance.timeout)

    @staticmethod
    def delete(path: str, params: dict = None) -> requests.Response:
        """
        Get a DELETE request.
        Arguments:
            path {str} -- The path to use.
            params {dict} -- The params to use.
        Returns:
            requests.Response -- The response.
        """
        request = Request('DELETE', HttpClient.__instance.host + path, params=params)
        prepare_request: PreparedRequest = HttpClient.__instance.session.prepare_request(request)
        return HttpClient.__instance.session.send(prepare_request, timeout=HttpClient.__instance.timeout)