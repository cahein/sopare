import os
import glob
import re
import time
from datetime import datetime
import json
import ecasound_handler
import logging

basefolder = os.path.dirname(os.path.realpath(__file__))

with open(basefolder + "/config.json") as config_file:
    config = json.load(config_file)


def get_path_from_spec(path_spec):
    path_type = path_spec['type']
    if path_type == 'relative':
        path = basefolder + '/' + path_spec['path']
    else:
        path = path_spec['path']
    return path


logLevel = 'DEBUG'
if config['log_level']:
    logLevel = config['log_level']

fh = logging.FileHandler('recorder.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s: %(message)s'
)
fh.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(fh)
logger.setLevel(logLevel)

eca = ecasound_handler.EcasoundHandler(logLevel)


if config['path_for_event_sounds']:
    path_spec_for_event_sounds = config['path_for_event_sounds']
    path_for_event_sounds = get_path_from_spec(path_spec_for_event_sounds)

if config['path_for_recordings_default']:
    path_for_recordings_default = config['path_for_recordings_default']
if config['path_for_recordings_fallback']:
    path_spec_for_recordings = config['path_for_recordings_fallback']
    path_for_recordings_fallback = get_path_from_spec(path_spec_for_recordings)

if (not os.path.exists(path_for_event_sounds)):
    print('ERROR: The path to store the sounds to be played as feedback '
          + ' to the user must be configured.')
if (not os.path.exists(path_for_recordings_fallback)):
    print('ERROR: The path to store the recording files must be configured.')

print('Path for event sounds: ' + path_for_event_sounds)
print('Default path for recordings: ' + path_for_recordings_default)
print('Fallback path for recordings: ' + path_for_recordings_fallback)


def handleTerm(term):
    logger.debug('Term recognized: ' + term)
    if term == 'aufnehmen':
        if (eca.get_engine_status() == 'running'):
            stopRecording()
            playTermSound('stop')
        else:
            playTermSound('aufnehmen')
            startRecording()
    elif term == 'abspielen':
        if isRecording():
            logger.debug('still recording')
        else:
            playLastRecording()


def playTermSound(term):
    soundfile = 'default.wav'
    if term == 'stop':
        soundfile = 'stop.wav'
    elif term == 'aufnehmen':
        soundfile = 'aufnehmen.wav'
    playSound(path_for_event_sounds + '/' + soundfile)


def playLastRecording():
    last_recording = getLastRecording()
    if last_recording != '':
        playSound(last_recording)


def playSound(soundfile):
    logger.info('play ' + soundfile)
    sound_length = eca.play_sound(soundfile)
    if (sound_length and sound_length > 10):
        logger.debug('going to sleep: ' + str(sound_length))
        time.sleep(sound_length)


def startRecording():
    filename = getRecordingFilename()
    logger.info('start recording ' + filename)
    eca.start_recording(filename)


def stopRecording():
    if isRecording():
        logger.info('stop recording')
        eca.stop_recording()


def isRecording():
    cs_connected = eca.get_connected_chainsetup()
    eca_status = eca.get_engine_status()
    if cs_connected == 'record-chainsetup' and eca_status == 'running':
        return True
    else:
        return False


def getLastRecording():
    latestDate = -1
    latestTime = -1
    path_for_recordings = getRecordingsPath()

    for recordedFile in glob.glob(path_for_recordings + "/recording.*.wav"):
        match = re.match(r'.*\/recording\.(\d+)-(\d+)\.wav', recordedFile)
        if match:
            d = match.group(1)
            t = match.group(2)
            if int(d) > latestDate:
                latestDate = int(d)
                latestTime = int(t)
            elif int(d) == latestDate:
                if int(t) > latestTime:
                    latestTime = int(t)

    if latestDate == -1:
        return ''
    else:
        return path_for_recordings + "/recording." \
            + str(latestDate) + "-" + str(latestTime) + ".wav"


def getRecordingFilename():
    dt = datetime.now()
    dtString = dt.strftime('%Y%m%d-%H%M%S')
    path_for_recordings = getRecordingsPath()

    return path_for_recordings + "/recording." + dtString + ".wav"


def getRecordingsPath():
    if (os.path.exists(path_for_recordings_default)):
        return path_for_recordings_default
    else:
        return path_for_recordings_fallback
