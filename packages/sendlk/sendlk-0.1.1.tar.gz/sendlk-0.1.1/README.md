# Send.lk Python SDK

sendlk is a python SDK for the [send.lk](https://send.lk) SMS getaway.

## Example

Here is an article of example, How to use this package with FastAPI -> [ishanga.hashnode.dev](https://ishanga.hashnode.dev/create-otpmobile-verification-api-with-python-fastapi-and-sendlk-sms-gateway)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install sendlk.

```bash
pip install sendlk
```
## Features
- Send Messages
- Send Verify Code (Package's feature)
- Validate Verify Code (Package's feature)
- Check Balance
- _TODO: Contacts_
- _TODO: Message History_

## Send Normal SMS

```python
import sendlk

# Befor import any module from sendlk you should initialize it first
# secret will use in the OTP/Phone number verify module
sendlk.initialize("sendlk-token", "my-custom-super-secret")

from sendlk.responses import SmsResponse, ProfileResponse
from sendlk.exceptions import SendLKException
from sendlk.engine import SMS, Profile

try:
    response: SmsResponse = SMS.send("07XXXXXXXX", "Hello World!", "SendTest")
    print(response)
except SendLKException as e:
    print(e)

```
## Send OTP/Verify Code
```python
from sendlk.responses import SmsResponse
from sendlk.exceptions import SendLKException
from sendlk.engine import SMS
from sendlk.options import SendLKVerifyOption, SendLKCodeTemplet

# If you want to use custom text/body you can create custom templet using "SendLKCodeTemplet"
# If code text templet not given default one will be used
# Default: "0000 is your verification code."
class CustomCodeTemplet(SendLKCodeTemplet):
    def __init__(self):
        super().__init__()
        
    def text(self, code: str) -> str:
        return f"{code} is the varification code for foo serveice."

# Create option object
options: SendLKVerifyOption = SendLKVerifyOption(
    code_length=6,
    expires_in=5,
    sender_id="SendTest",
    code_templet=CustomCodeTemplet()
)

try:
    response = SMS.send_verify_code("07XXXXXXXX", options)
    token = response.data.get("token", None)
    code = input("Enter the code: ")
    response = SMS.validate_verify_code(code, token)
    print(response)
except SendLKException as e:
    print(e)

```
## Check remaining balance
```python
import sendlk

# Befor import any module from sendlk you should initialize it first
# secret will use in the OTP/Phone number verify module
sendlk.initialize("sendlk-token", "my-custom-super-secret")

from sendlk.responses import SmsResponse, ProfileResponse
from sendlk.exceptions import SendLKException
from sendlk.engine import SMS, Profile

try:
    response: ProfileResponse = Profile.balance()
    print(response.remaining)
except SendLKException as e:
    print(e)

```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)