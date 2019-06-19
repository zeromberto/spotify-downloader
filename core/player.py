import os
import threading
import time

from core.const import log
from core.record import record
from mopidy_json_client import MopidyClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caching_enabled = False


class ReadWriteLock(object):
    """ A lock object that allows many simultaneous "read locks", but
    only one "write lock." """

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self):
        """ Acquire a read lock. Blocks only if a thread has
        acquired the write lock. """
        self._read_ready.acquire()
        try:
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        """ Release a read lock. """
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notifyAll()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        """ Acquire a write lock. Blocks until there are no
        acquired read or write locks. """
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        """ Release a write lock. """
        self._read_ready.release()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PlayerListener(metaclass=Singleton):
    def __init__(self):
        self.record_thread = None
        self.mutex = ReadWriteLock()
        self.playback_stopped = False
        self.filename = ''
        self.songname = ''
        self.play_time = 0

    def get_playback_stopped(self):
        self.mutex.acquire_read()
        stopped = self.playback_stopped
        self.mutex.release_read()
        return stopped

    def mopidy_playback_stopped(self):
        self.play_time = time.time() - self.play_time
        self.mutex.acquire_write()
        self.playback_stopped = True
        self.mutex.release_write()
        log.debug('stopped playback')

    def mopidy_playback_started(self):
        self.play_time = time.time()
        self.mutex.acquire_write()
        self.playback_stopped = False
        self.mutex.release_write()
        log.debug('started playback')

    def start_recording(self):
        log.debug('start recording')
        self.record_thread = threading.Thread(
            target=record,
            args=[self.filename, self.songname, self.get_playback_stopped])
        self.record_thread.start()

    def reset_play_time(self):
        log.debug('resetting play time')
        self.play_time = 0


mopidy_debug = True if os.getenv('MOPIDY_DEBUG') else False
client = MopidyClient(debug=mopidy_debug)
listener = PlayerListener()


# def mopidy_playback_state_changed(old_state, new_state):
#     if new_state == 'stopped' and old_state == 'playing':
#         listener.mopidy_playback_stopped()


def playback_started(tl_track):
    listener.mopidy_playback_started()


def playback_ended(tl_track, time_position):
    listener.mopidy_playback_stopped()


client.bind_event('track_playback_started', playback_started)
client.bind_event('track_playback_ended', playback_ended)
# client.bind_event('playback_state_changed', mopidy_playback_state_changed)


def play_and_record(track_uri="spotify:track:1L1dpImK36DoZPr7rxy0hJ", filename="foo", songname="bar"):
    log.debug("entered playing and record")
    client.playback.stop()
    client.tracklist.set_repeat(False)
    client.tracklist.clear()
    client.tracklist.set_single(True)
    client.mixer.set_mute(False)
    client.mixer.set_volume(100)
    client.tracklist.add(uri=track_uri)
    listener.filename = filename
    listener.songname = songname

    try:
        # Activate cache
        if caching_enabled:
            log.debug('caching start')
            client.playback.play()
            timeout = time.time() + 20
            while listener.get_playback_stopped():
                if time.time() > timeout:
                    raise RuntimeWarning('Could not play track for caching {}'.format(songname))
                time.sleep(0.05)
            time.sleep(3)
            log.debug('stopping cache play')
            client.playback.stop()
            timeout = time.time() + 20
            while not listener.get_playback_stopped():
                if time.time() > timeout:
                    raise RuntimeWarning('Caching record took too long {}'.format(songname))
                time.sleep(0.05)
            log.debug('caching end')

        # start recording
        listener.reset_play_time()
        listener.start_recording()
        # make sure thread has started
        timeout = time.time() + 15
        while not listener.record_thread.is_alive():
            if time.time() > timeout:
                raise RuntimeError('Record thread still not alive track {}'.format(songname))

        time.sleep(3)
        client.playback.play()
        timeout = time.time() + 10
        while listener.get_playback_stopped():
            if time.time() > timeout:
                raise RuntimeWarning('Could not play track {}'.format(songname))
            time.sleep(0.05)

        # wait for end
        timeout = time.time() + 60 * 20
        while not listener.get_playback_stopped():
            if time.time() > timeout:
                raise RuntimeWarning('Record took longer than 20 minutes track {}'.format(songname))
            time.sleep(0.1)

        # make sure thread has stopped
        timeout = time.time() + 15
        while listener.record_thread.is_alive():
            if time.time() > timeout:
                raise RuntimeError('Record thread still alive track {}'.format(songname))

    except RuntimeWarning as e:
        log.error(str(e))
    finally:
        client.playback.stop()
        return listener.play_time
