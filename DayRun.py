import time
from datetime import datetime
import sched
from scrapy import cmdline


def perform_task():
    scheduler.enter(60*60*24, 0, perform_task)
    cmdline.execute('scrapy crawl music'.split())


if __name__ == '__main__':
    scheduler = sched.scheduler(time.time, time.sleep)
    now = datetime.now()
    sched_time = datetime(now.year, now.month, now.day, 0, 0, 0)
    if sched_time < now:
        sched_time = sched_time.replace(day=now.day+1)
    scheduler.enterabs(sched_time.timestamp(), 0, perform_task)  # datetime.timestamp()是python3.3后才有
    scheduler.run()
