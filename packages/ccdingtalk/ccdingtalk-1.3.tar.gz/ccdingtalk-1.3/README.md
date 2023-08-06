# Install

```
pip3 install ccdingtalk --upgrade --user
```


# Send Message

```
chat_bot = DingTalkWebhookMessage(webhook_url)
r = chat_bot.send_text(msg=msg, at_mobiles=at_mobiles)
```


# Send with several webhooks (auto load balance)


```
import ccdingtalk

def __webhook_urls() -> list:
    api = 'https://oapi.dingtalk.com/robot/send?access_token='
    tokens = [
        'token1',
        'token2',
        'token3',
        'token4',
        'token5',
    ]
    results = []
    for token in tokens:
        results.append(api + token)
    return results


__shared_msg_queue = DingTalkWebhookMessageQueue(__webhook_urls())


def send_ding_msg(msg: str, at_mobile=''):
    __shared_msg_queue.add_message(msg, [at_mobile])
```

# Reply Message


```
class DingBotRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
		response = DingTalkReply.text_msg("This is GET request")
		response_bytes = response.encode()
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.send_header("Content-Length", str(len(response_bytes)))
		self.end_headers()
		self.wfile.write(response_bytes)

    def do_POST(self):
		response = DingTalkReply.text_msg("This is POST request")
		response_bytes = response.encode()
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.send_header("Content-Length", str(len(response_bytes)))
		self.end_headers()
		self.wfile.write(response_bytes)
```