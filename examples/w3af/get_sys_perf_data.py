#!/usr/bin/python
import os

import psutil
import json

netinfo = psutil.net_io_counters(pernic=True)
for key, value in netinfo.iteritems():
    netinfo[key] = value._asdict()

psutil_data = {'CPU': psutil.cpu_times()._asdict(),
               'Load average': os.getloadavg(),
               'Virtual memory': psutil.virtual_memory()._asdict(),
               'Swap memory': psutil.swap_memory()._asdict(),
               'Network': netinfo}

data_as_json = json.dumps(psutil_data, sort_keys=True, indent=4)
file('/tmp/collector/w3af-psutil.data', 'w').write(data_as_json)