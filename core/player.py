import os
import threading
import time

from core.const import log
from core.record import record
from mopidy_json_client import MopidyClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PlayerListener(object):
    playback_stopped = False
    filename = ''
    songname = ''

    def get_playback_stopped(self):
        return self.playback_stopped

    def mopidy_playback_stopped(self):
        log.debug('stopped playback')
        self.playback_stopped = True

    def mopidy_playback_started(self):
        log.debug('started playback')
        self.playback_stopped = False
        self.start_recording()

    def start_recording(self):
        log.debug('start recording')
        record(self.filename, self.songname, self.get_playback_stopped)


def play_and_record(track_uri="spotify:track:1L1dpImK36DoZPr7rxy0hJ", filename="foo", songname="bar"):
    log.debug("entered playing and record")
    client = MopidyClient(debug=True)
    listener = PlayerListener()
    listener.filename = filename
    listener.songname = songname

    def mopidy_playback_state_changed(old_state, new_state):
        log.debug("received event")
        if new_state == 'stopped' and old_state == 'playing':
            listener.mopidy_playback_stopped()

    client.bind_event('playback_state_changed', mopidy_playback_state_changed)

    client.playback.stop()
    client.tracklist.set_repeat(False)
    client.tracklist.clear()
    client.mixer.set_mute(False)
    client.mixer.set_volume(100)
    client.tracklist.add(uri=track_uri)
    # threading.Thread(target=).start()
    # time.sleep(0.05)
    client.playback.play()
    listener.mopidy_playback_started()
    while not listener.get_playback_stopped():
        time.sleep(0.01)
    time.sleep(1)
