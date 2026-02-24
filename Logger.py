import logging
import datetime as dt

date = dt.datetime.now().strftime("%y%m%d")


logging.basicConfig(
                    filename=f"logs/{date}.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(filename)s>%(funcName)s %(message)s'
                    )
