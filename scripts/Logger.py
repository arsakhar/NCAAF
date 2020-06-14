import time
import datetime

class Logger:
    def __init__(self):
        pass

    def log_query_time(self, tag, start_time, end_time):
        with open("../LogFile.txt", "a") as logfile:
            logfile.write(self.get_timestamp()
                          + ": "
                          + tag
                          + str(end_time - start_time)
                          + " seconds"
                          + "\n")

    def log(self, output):
        with open("../LogFile.txt", "a") as logfile:
            logfile.write(self.get_timestamp()
                                  + ": "
                                  + output
                                  + "\n")

    def get_timestamp(self):
        ts = time.time()
        dt = datetime.datetime
        timestamp = dt.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        return timestamp
