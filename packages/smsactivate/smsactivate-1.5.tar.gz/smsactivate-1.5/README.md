### Installation smsactivate
```sh
pip install smsactivate
```
## Requires 
- requests
- json

### Connection

```python
from smsactivate.api import SMSActivateAPI
sa = SMSActivateAPI(APIKEY)
sa.debug_mode = True # Optional action. Required for debugging
```
Description of the functionality of smsactivate is indicated on the [SMSActivate API](https://sms-activate.org/api2)