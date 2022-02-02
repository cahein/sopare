# Recorder SoPaRe Plugin

This plugin is a speech-controlled voice recorder. It is developed for my mother in law, who is visually handicapped and cannot use devices with small buttons any more.
SoPaRe allows sound recognition without a connection to the internet, and therefore protects the privacy of users. It runs on a Raspberry Pi with a USB microphone and speakers.

The recorder is controlled by only two terms, **aufnehmen** (record) und **abspielen** (play).

The **aufnehmen** either starts or stops the recording. When not recording, it will play 'sounds/aufnehmen.wav' and start recording. When recording, it will play 'sounds/stop.wav' and stop recording.

The 'abspielen' plays the last minute of the last recording.

## Systemd

The recorder may best use the JACK Audio Connection Kit, but also works with PulseAudio. Note, that running SoPaRe without user login, PulseAudio needs to run as a system service.

To start SoPaRe on boot, the following sopare.service specification may be used. Because SoPaRe needs to be started in '--loop' mode, the Linux **daemonize** tool is being used.

    [Unit]
    Description=SoPaRe Speech Recorder
    After=pulseaudio.service

    [Service]
    Type=forking
    ExecStart=daemonize -a -E TERM=xterm -u username -c /home/username/projects/sopare -e /home/username/projects/sopare.err -o /home/username/projects/sopare.log -p /home/username/projects/sopare.pid -v /usr/local/bin/startSopare
    PIDFile=/home/username/projects/sopare.pid
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

## Misc

Copy all relevant files to some folder for deployment.

rsync -avz --exclude '*~' --exclude '#*' --exclude '.git' --exclude '*.pyc' --exclude 'dict' --exclude '__pycache__' --dry-run /path/to/dev/sopare hostname:/path/to/sopare/
