from describer_functions import send_tel_update, update_error_log, main
from datetime import datetime as dt
import traceback

current_hour = dt.utcnow().hour

try:
    if current_hour in [1, 17]:  # Allows you to change post frequency without updating cron (w/ cron calling hourly)
        main()
except Exception as e:
    x = str(e)
    y = ''.join(traceback.format_exc())
    send_tel_update('Describer encountered an error.')
    update_error_log('Describer' + x+y)
