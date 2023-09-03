# boot.py -- run on boot-up
import esp
esp.osdebug(None)

import gc
gc.collect()
