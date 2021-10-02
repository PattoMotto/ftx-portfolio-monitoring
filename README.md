# ftx-portfolio-monitoring

### Prerequisite
1) Google sheet and drive credential (json)
2) FTX api_key and secret for main account (read_only)
3) Python 3.9.5

### Install dependencies
```
pip install -r requirements.txt
```

### Configuration
1) Rename `example.portfolio_monitoring_bot.config` to `portfolio_monitoring_bot.config`
2) Update configuration
```
{
    "apiKey": "", << Main account (read only)
    "secret": "", << Main account (read only)
    "googleCredential": "project-crypto-currency.json", << file name of credential downloaded from google console
    "gSheetName": "Portfolio monitoring", << google sheet name
    "sleepTimeSecond": 3600 << bot sleep duration
}
```

### Run bot
```
python start_bot.py
```

### Use case 1 visualize on [data studio](https://datastudio.google.com)
<img width="1204" alt="image" src="https://user-images.githubusercontent.com/1745000/135710488-18d6f3b7-2d67-4a95-9344-226def080ba9.png">
<img width="1201" alt="image" src="https://user-images.githubusercontent.com/1745000/135710553-94206175-f48c-4ab7-91fa-fc484f273851.png">
