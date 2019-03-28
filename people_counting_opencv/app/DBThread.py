import datetime
import time
from threading import Thread

from .ApplicationContext import ApplicationContext


class DBThread(Thread):
    def __init__(self, time_interval, in_min="True"):
        Thread.__init__(self)
        self.is_running = True
        self.setDaemon(True)
        if in_min == "True" or in_min == "true" or in_min == 1:
            in_min = True
        else:
            if in_min == "False" or in_min == "false" or in_min == 0:
                in_min = False
            else:
                raise Exception("Invalid Value")
        self.set_time_interval(time_interval=time_interval, in_min=in_min)

    # def insert_into_db(self):
    #     app_props = ApplicationContext.getApplicationContext()
    #     db_connector = app_props.db_connector
    #     db_connector.collection.insert_one({"count": app_props.total_count, "date": datetime.datetime.utcnow()})

    def set_time_interval(self, time_interval, in_min=True):
        if in_min:
            self.time_interval = time_interval * 60
        else:
            self.time_interval = time_interval

    def stop_db_thread(self):
        self.is_running = False

    def run(self):
        app_context = ApplicationContext.getApplicationContext()
        db_connector = app_context.db_connector
        while self.is_running:
            db_connector.collection.insert_one({"count": app_context.total_count, "date": datetime.datetime.utcnow()})
            app_context.total_count = 0
            time.sleep(self.time_interval)

    # def run_db_thread(self):
    #     app_props = ApplicationContext.getApplicationContext()
    #     db_connector = app_props.db_connector
    #     db_connector.collection.insert_one({"count": app_props.total_count, "date": datetime.datetime.utcnow()})
    #     if self.is_running:
    #         threading.Timer(self.time_interval,self.run_db_thread).start()
    #     else:
    #         return
