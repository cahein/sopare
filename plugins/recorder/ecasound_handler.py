import pyeca
import time


class EcasoundHandler:
    def __init__(self):
        print('Initialize Ecasound Control Interface')
        self.ecaiam = pyeca.ECA_CONTROL_INTERFACE()
        self.ecaiam.command('cs-add play-chainsetup')
        self.ecaiam.command('c-add play-chain')
        self.ecaiam.command('ao-add alsa')

        self.ecaiam.command('cs-add record-chainsetup')
        self.ecaiam.command('c-add record-chain')
        self.ecaiam.command('ai-add alsa')
        self.ecaiam.command('cop-add -ea:200')
        # self.ecaiam.command('cs-set-audio-format 16,2,44100')

    def play_sound(self, soundfile):
        print('prepare ' + soundfile)
        self.ecaiam.command('cs-select play-chainsetup')
        self.ecaiam.command('c-select play-chain')
        self.ecaiam.command('ai-add ' + soundfile)

        connected = self.ecaiam.command('cs-connect')
        print('chainsetup connected? ' + str(connected))
        self.ecaiam.command('start')

        self.ecaiam.command('cs-get-length')
        length = self.ecaiam.last_float()
        print('length of sound: ' + str(length))
        
        while 1:
            time.sleep(1)
            self.ecaiam.command('engine-status')
            status = self.ecaiam.last_string()
            print('engine status: ' + status)
                
            if status == 'not started' or status == 'finished':
                self.ecaiam.command('stop')
                self.ecaiam.command('ai-remove')
                self.ecaiam.command('cs-disconnect')
                print('chainset disconnected')
                return length;
                break

    def start_recording(self, filename):
        self.ecaiam.command('cs-select record-chainsetup')
        self.ecaiam.command('c-select record-chain')
        self.ecaiam.command('cs-set-position 0')
        self.ecaiam.command('cs-set-length 1800')

        print('recording to ' + filename)
        self.ecaiam.command('ao-add ' + filename)
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
