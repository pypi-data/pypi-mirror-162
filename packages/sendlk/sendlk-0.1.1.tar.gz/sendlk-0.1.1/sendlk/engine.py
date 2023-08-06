import json
from requests.models import HTTPError, Response
from sendlk.responses import ProfileResponse, SmsResponse
from sendlk.exceptions import SendLKException
from sendlk.options import SendLKVerifyOption
from sendlk._utils import encrypt_token, decrypt_token
import re

from sendlk import _client

_SEND_PATH = "sms/send"
_BALANCE_PATH = "balance"
_HTTP_CLIENT = _client.HttpClient.get_instance()
_REGEX_PHONE_NUMBER = re.compile(r"^(?:0|94|\+94|0094)?(?:(11|21|23|24|25|26|27|31|32|33|34|35|36|37|38|41|45|47|51|52|54|55|57|63|65|66|67|81|91)(0|2|3|4|5|7|9)|7(0|1|2|4|5|6|7|8)\d)\d{6}$")

class SMS:
    @classmethod
    def _validate_number(cls, number: str) -> str:
        """
        Validate the phone number.
        """
        if number is None or not isinstance(number, str):
            raise SendLKException(message="Invalid number")
        if not _REGEX_PHONE_NUMBER.match(number):
            raise SendLKException(message=f"Invalid phone number: {number}")
        return number
    
    @classmethod
    def _validate_text(cls, text: str) -> str:
        """
        Validate the text.
        """
        if text is None or not isinstance(text, str):
            raise SendLKException(message="Invalid text")
        if len(text) > 160:
            raise SendLKException(message="Text is too long")
        return text
    
    @classmethod
    def _validate_sender_id(cls, sender_id: str) -> str:
        """
        Validate the sender id.
        """
        if sender_id is None or not isinstance(sender_id, str):
            raise SendLKException(message="Invalid sender id")
        if len(sender_id) > 11:
            raise SendLKException(message="Sender id is too long")
        return sender_id
    
    @classmethod
    def get_status(cls, uid: str) -> SmsResponse:
        """
        Get the status of a message.
        """
        if uid is None or not isinstance(uid, str):
            raise SendLKException(message="Invalid uid")
        try:
            response: Response = _HTTP_CLIENT.get(f"{_SEND_PATH}/{uid}")
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("status", None) == "success":
                return SmsResponse(message=response_data.get("message", None), data=response_data.get("data"))

            else:
                raise SendLKException(message=response_data.get("message", None))
        except SendLKException as e:
            raise e
        except HTTPError as e:
            error = {}
            try:
                error = json.loads(e.response.text)
            except:
                raise SendLKException(message=str(e.response.text))
            raise SendLKException(message=error.get("message", str(error))) from e
        except Exception as e:
            raise SendLKException(message=str(e)) from e

    
    @classmethod
    def send(cls, number: str, text: str, sender_id: str) -> SmsResponse:
        """
        Send an SMS.
        Arguments:
            number {str} -- The number to send to.
            text {str} -- The text to send.
            sender {str} -- The sender id to use.
        Returns:
            SmsResponse -- The response.
        Raises:
            SendLKException -- If the args not valid.
            Exception: If the response is not a valid.
        """
        number = cls._validate_number(number)
        text = cls._validate_text(text)
        sender_id = cls._validate_sender_id(sender_id)
        data = {"recipient": number, "sender_id": sender_id, "message": text}
        response_data = {}
        try:
            response: Response = _HTTP_CLIENT.post(path=_SEND_PATH, data=data)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("status", None) == "success":
                return SmsResponse(message=response_data.get("message", None), data=response_data.get("data"))

            else:
                raise SendLKException(message=response_data.get("message", None))
        except SendLKException as e:
            raise e
        except HTTPError as e:
            error = {}
            try:
                error = json.loads(e.response.text)
            except:
                raise SendLKException(message=str(e.response.text))
            raise SendLKException(message=error.get("message", str(error))) from e
        except Exception as e:
            raise SendLKException(message=str(e)) from e

    @classmethod
    def send_verify_code(cls, number: str, verify_option: SendLKVerifyOption) -> SmsResponse:
        """
        Send a verify code to a number.
        Arguments:
            number {str} -- The number to send to.
            verify_option {SendLKVerifyOption} -- The verify option to use.
        Returns:
            SmsResponse -- The response.
        Raises:
            SendLKException -- If the args not valid.
            Exception: If the response is not a valid.
        """
        number = cls._validate_number(number)
        if verify_option is None or not isinstance(verify_option, SendLKVerifyOption):
            raise SendLKException(message="Invalid verify option")
        token = ""
        try:
            token, code = encrypt_token(length=verify_option.code_length, expire=verify_option.expires_in)

            text = verify_option.get_text(code)
            response = cls.send(number=number, text=text, sender_id=verify_option.sender_id)

            response.add_data(key="token", value=token)
            return response
        except SendLKException as e:
            raise e
        except Exception as e:
            raise SendLKException(message=str(e)) from e
    
    @classmethod
    def validate_verify_code(cls, code: str, token: str) -> SmsResponse:
        """
        Validate a verify code.
        Arguments:
            code {str} -- The code to validate.
            token {str} -- The token to validate.
        Returns:
            SmsResponse -- The response.
        Raises:
            SendLKException -- If the args not valid.
            Exception: If the response is not a valid.
        """
        if code is None or not isinstance(code, str):
            raise SendLKException(message="Invalid code")
        if token is None or not isinstance(token, str):
            raise SendLKException(message="Invalid token")
        try:
            code = decrypt_token(token=token, verify_code=code)
            return SmsResponse(message="Code is valid", data={"code": code})
        except SendLKException as e:
            raise e
        except Exception as e:
            raise SendLKException(message=str(e)) from e
        
class Profile:
    @classmethod
    def balance(cls) -> ProfileResponse:
        """
        Get the balance.
        Returns:
            ProfileResponse -- The response.
            ProfileResponse.remaining: int = The remaining balance.
            ProfileResponse.used: int = The used balance.
            ProfileResponse.expired_on: str = The date when the balance expires.
        Raises:
            SendLKException -- If the response is not a valid.
        """
        response: Response = _HTTP_CLIENT.get(_BALANCE_PATH)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status", None) == "success":
            return ProfileResponse(message=response_data.get("message", None), data=response_data.get("data"))

        else:
            raise SendLKException(message=response_data.get("message", None))