# Hackle Sdk For Python

## Install

```
pip install hackle-sdk
```

## Usage
### Import
```
from hackle import hackle
```

### Close
```
import atexit

@atexit.register
def __exit__():
    hackle_client.close()
```

### User
```
from hackle.model import Hackle

user = Hackle.user('ae2182e0')

user = Hackle.user(id='ae2182e0', app_version='1.0.1', age=23, paying_customer=True)
```

### Get Variation
```
from hackle.model import Hackle

user = Hackle.user(id='DEVICE_ID')
hackle_client.variation(experiment_key=42, user=user)
```

### Track Event
```
event = Hackle.event('purchase')
event = Hackle.event('purchase', value=32000)
event = Hackle.event(key='purchase', value=32000, first_paying=False, app_version='1.0.1', item_count=5)

hackle_client.track(event, user)
```
