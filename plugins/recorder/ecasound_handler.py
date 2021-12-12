import pyeca
import time


class EcasoundHandler:
    def __init__(self):
        print('Initialize Ecasound Control Interface')
        self.ecaiam = pyeca.ECA_CONTROL_INTERFACE()
        self.ecaiam.command('cs-add play-chainsetup')
        self.ecaiam.command('c-add default-chain')
        self.ecaiam.command('ao-add alsa')

        self.ecaiam.command('cs-add record-chainsetup')
        self.ecaiam.command('c-add default-chain')
        self.ecaiam.command('ai-add alsa')

    def play_sound(self, soundfile):
        print('play ' + soundfile)

        self.ecaiam.command('cs-select play-chainsetup')
        self.ecaiam.command('c-select default-chain')

        self.ecaiam.command('ai-add ' + soundfile)

        self.ecaiam.command('cs-connect')
        self.ecaiam.command('cs-get-length')
        length = self.ecaiam.last_float()

        self.ecaiam.command('start')

        while 1:
            time.sleep(1)
            self.ecaiam.command('engine-status')
            status = self.ecaiam.last_string()
            if status == 'finished':
                print('engine-status finished')
                self.ecaiam.command('stop')
                self.ecaiam.command('ai-remove')
                self.ecaiam.command('cs-disconnect')
                print('chainset disconnected')
                return length
                break

    def start_recording(self, filename):
        self.ecaiam.command('cs-select record-chainsetup')
        self.ecaiam.command('c-select default-chain')

        print('recording to ' + filename)
        self.ecaiam.command('ao-add ' + filename)

        # self.ecaiam.command('cop-add -ea:100')
        self.ecaiam.command('cs-connect')
        self.ecaiam.command('start')

    def stop_recording(self):
        self.ecaiam.command('stop')
        self.ecaiam.command('ao-remove')
        self.ecaiam.command('cs-disconnect')

    def get_engine_status(self):
        self.ecaiam.command('engine-status')
        status = self.ecaiam.last_string()
        print('engine-status:' + status)
        return status

    def get_connected_chainsetup(self):
        self.ecaiam.command('cs-connected')
        cs_connected = self.ecaiam.last_string()
        print('connected chainsetup:' + cs_connected)
        return cs_connected
