from apscheduler.schedulers.blocking import BlockingScheduler
from pmPortfolioMonitoringBot import PortfolioMonitoringBot
import json

# Load local config
configFile = open('portfolio_monitoring_bot.config')
jsonConfig = json.load(configFile)
# api and secret
apiKey = jsonConfig['apiKey']
secret = jsonConfig['secret']
sleepTimeSecond = int(jsonConfig['sleepTimeSecond'])

monitoringBot = PortfolioMonitoringBot(
    apiKey=apiKey,
    secret=secret,
    gSheetName=jsonConfig['gSheetName'],
)
monitoringBot.loop()
scheduler = BlockingScheduler(job_defaults= {'max_instances': 1})
scheduler.add_job(monitoringBot.loop, 'interval', seconds=sleepTimeSecond)
scheduler.start()