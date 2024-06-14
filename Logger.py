import logging
import datetime as dt
date = f"{dt.datetime.now().year[-2]:02d}{dt.datetime.now().month:02d}{dt.datetime.now().day[-2]:02d}"


logging.basicConfig(
                    filename=date, 
                    level=logging.DEBUG,
                    format='%'
                    )