import os
import glob
import re
import time
from datetime import datetime
import json
import ecasound_handler

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


if config['path_for_recordings']:
    path_spec_for_recordings = config['path_for_recordings']
    path_for_recordings = get_path_from_spec(path_spec_for_recordings)

if config['path_for_event_sounds']:
    path_spec_for_event_sounds = config['path_for_event_sounds']
    path_for_event_sounds = get_path_from_spec(path_spec_for_event_sounds)


if (not os.path.exists(path_for_event_sounds)):
    print('ERROR: The path to store the sounds to be played as feedback to the user must be configured.')
if (not os.path.exists(path_for_recordings)):
    print('ERROR: The path to store the recording files must be configured.')

print('Path for recordings: ' + path_for_recordings)
print('Path for event sounds: ' + path_for_event_sounds)


eca = ecasound_handler.EcasoundHandler()


def handleTerm(term):
    if not isRecording():
        if term == 'stop':
            return

    if term == 'aufnehmen':
        if eca.get_engine_status() == 'not started':
            playTermSound('aufnehmen')
            startRecording()
    elif term == 'stop':
        stopRecording()
        playTermSound('stop')
    elif term == 'abspielen':
        if isRecording():
            print('still recording')
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
    length = eca.play_sound(soundfile)
    print('go to sleep ' + str(length))
    time.sleep(length)


def startRecording():
    filename = getRecordingFilename()
    eca.start_recording(filename)


def stopRecording():
    if isRecording():
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
    return path_for_recordings + "/recording." + dtString + ".wav"
