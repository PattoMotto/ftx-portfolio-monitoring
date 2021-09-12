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