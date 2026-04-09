# ~/klipper/klippy/extras/esp32_chamber.py
import logging
import requests

class ESP32ChamberSensor:
    def __init__(self, config):
        self.temp = self.min_temp = self.max_temp = self.humidity = 0.0
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        self.url = config.get('url')
        self.sample_timer = self.reactor.register_timer(self._update)
        logging.info("[ESP32Chmaber]: name %s", self.name)
        self.printer.add_object("esp32_chamber " + self.name, self)
        self.printer.register_event_handler("klippy:ready", self.handle_connect)

    def handle_connect(self):
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW + 5)

    def _update(self, eventtime):
        try:
            data = requests.get(self.url, timeout=2).json()
            self.temp = float(data.get("temp", 0))
            self.humidity = float(data.get("humid", 0))
            #logging.info("[ESP32Chamber]: temp: %.2f, humid: %.2f", self.temp, self.humidity)
            if self._callback:
                self._callback(eventtime, self.temp)
        except Exception as e:
            logging.error("ESP32 chamber sensor error: %s", e)
        return eventtime + 5.0  # poll every 5s

    def get_report_time_delta(self):
        return 5.0

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_status(self, eventtime):
        #logging.info("[ESP32Chamber] GET_STATUS CALLED temp=%.2f, humid: %.2f", self.temp, self.humidity)
        data = {
           'temperature': self.temp,
           'humidity': self.humidity,
        }
        return data

def load_config(config):
    # Register sensor
    pheaters = config.get_printer().lookup_object("heaters")
    pheaters.add_sensor_factory("esp32_chamber", ESP32ChamberSensor)

