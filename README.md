
# Discord RAT

## Setup

Install library

```shell
pip install -r requirements.txt
```
or
```shell
pip3 install -r requirements.txt
```

Put your bot token in 

```python
token = ""
bot.run(token)
```
or using token from environment
```python
from dotenv import load_dotenv
load_dotenv('.env')
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
```

Enjoy.
