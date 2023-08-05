# Pytest-Message

Pytest-message is a pytest extension for reporting to various messangers.

Pytest-message gives an ability to send report message of test status for only marked tests.

### Installation
```shell
pip install pytest-message
```

### Example
Currently `pytest-message` integrates with slack only(other popular messengers integration in progress) 

In order to receive messages you need to define listener and pass list of listeners to `notify` decorator
```python
from pytest_message.listeners import SlackListener
from pytest_message import notify


slack_listener = SlackListener(token="slack_secret_token", chat='chat_id')


@notify([slack_listener])
def test_sum():
    assert 1 + 1 == 2
```

You may pass as much listeners as you want to get report messages to all listeners.

#### SlackListener
SlackListener constructor takes **required**: `token, chat` and **optional**:  `on_error_add` fields.
- `token` - slack token
- `chat` - slack chat id
- `on_error_add`_[Optional]_ - takes string which will be added after failed or skipped test function name in main thread.
 Is nice for tagging responsible person if required or add any custom comment.



### Launch

In order to start tests with Pytest-Message you must provide `--notify` flag:
```shell
pytest tests --notify
```
