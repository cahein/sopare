import pyeca
import time
import logging


class EcasoundHandler:
    def __init__(self, logLevel):
        fh = logging.FileHandler('recorder.log')
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s'
        )
        fh.setFormatter(formatter)

        logger = logging.getLogger(__name__)
        logger.addHandler(fh)
        logger.setLevel(logLevel)

        logger.info('Initialize Ecasound Control Interface')
        self.logger = logger
        self.ecaiam = pyeca.ECA_CONTROL_INTERFACE(0)
        self.ecaiam.command('cs-add play-chainsetup')
        self.ecaiam.command('c-add play-chain')
        self.ecaiam.command('ao-add alsa')
        self.ecaiam.command('cs-set-audio-format 16,2,44100')

        self.ecaiam.command('cs-add record-chainsetup')
        self.ecaiam.command('c-add record-chain')
        self.ecaiam.command('ai-add alsa')
        self.ecaiam.command('cop-add -ea:200')
        self.ecaiam.command('cs-set-audio-format 16,1,44100')

    def play_sound(self, soundfile):
        current_selected = self.get_selected_chainsetup()
        if current_selected == 'record-chainsetup':
            status = self.get_engine_status()
            self.logger.debug('record-chainsetup engine-status: ' + status)

        self.ecaiam.command('cs-select play-chainsetup')
        self.ecaiam.command('c-select play-chain')
        self.ecaiam.command('ai-add ' + soundfile)

        connect_error = self.ecaiam.command('cs-connect')
        if connect_error:
            self.logger.error('playback - chainsetup connection error: '
                              + str(connect_error))
            self.ecaiam.command('ai-remove')
            return False

        self.ecaiam.command('cs-get-length')
        length = self.ecaiam.last_float()
        self.logger.debug('length of sound: ' + str(length))
        if length > 100:
            start_position = length - 60
            self.ecaiam.command('cs-set-position ' + str(start_position))

        self.ecaiam.command('start')

        while 1:
            time.sleep(1)

            status = self.get_engine_status()
            if status == 'not started' or status == 'finished':
                self.ecaiam.command('stop')
                self.ecaiam.command('ai-remove')
                self.ecaiam.command('cs-disconnect')
                self.logger.info('chainset disconnected')
                return length

    def start_recording(self, filename):
        self.ecaiam.command('cs-select record-chainsetup')
        self.ecaiam.command('c-select record-chain')
        self.ecaiam.command('cs-set-position 0')
        self.ecaiam.command('cs-set-length 1800')

        self.ecaiam.command('ao-add ' + filename)

        connect_error = self.ecaiam.command('cs-connect')
        if connect_error:
            self.logger.error('recording - chainsetup connection error: '
                              + str(connect_error))
            return
        self.ecaiam.command('start')

    def stop_recording(self):
        self.ecaiam.command('stop')
        self.ecaiam.command('ao-remove')
        self.ecaiam.command('cs-disconnect')
        self.logger.info('chainsetup stopped and disconnected')

    def get_engine_status(self):
        self.ecaiam.command('engine-status')
        status = self.ecaiam.last_string()
        self.logger.debug('engine-status: ' + status)
        return status

    def get_connected_chainsetup(self):
        self.ecaiam.command('cs-connected')
        cs_connected = self.ecaiam.last_string()
        self.logger.debug('connected chainsetup: ' + cs_connected)
        return cs_connected

    def get_selected_chainsetup(self):
        self.ecaiam.command('cs-selected')
        cs_selected = self.ecaiam.last_string()
        self.logger.debug('selected chainsetup: ' + cs_selected)
        return cs_selected
