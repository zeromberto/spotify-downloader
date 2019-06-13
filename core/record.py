import datetime
import os
import re
import subprocess
import time
from math import isclose

from core.const import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def record(file_name, track_name, stop_recording_handler):
    log.info('Recording {} to {}'.format(track_name, file_name))
    try:
        FNULL = open(os.devnull, 'w')
        record_process = subprocess.Popen(
            ['ffmpeg', '-f', 'pulse', '-i', 'default', '-b:a', '320k', '-f', 'mp3', file_name],
            stdout=FNULL, stderr=subprocess.STDOUT)
        log.debug('started recording')
        while not stop_recording_handler():
            time.sleep(0.01)
        log.debug('finished')
        record_process.terminate()
    except Exception as e:
        log.error(repr(e))
    finally:
        if record_process:
            record_process.kill()
    log.info('Finished recording of {}'.format(track_name))


def verify_length(file_name, duration, tolerance=3.0):
    ffmpeg_get_mediafile_length = [
        'sh', '-c', 'ffmpeg -i "$1" 2>&1 | grep Duration',
        '_', file_name]
    try:
        output = subprocess.Popen(ffmpeg_get_mediafile_length, stdout=subprocess.PIPE).stdout.read()
        real_duration = re.findall(r'(?<=Duration: )(.*?)(?=,)', str(output))[0]
        real_duration = time.strptime(real_duration.split('.')[0], '%H:%M:%S')
        real_duration_sec = datetime.timedelta(hours=real_duration.tm_hour,
                                               minutes=real_duration.tm_min,
                                               seconds=real_duration.tm_sec).total_seconds()
        log.debug('Recorded {} secs and track is set to {} secs at spotify'.format(real_duration_sec, duration))
    except Exception as e:
        log.error(repr(e))
        return False

    if not isclose(real_duration_sec, duration, abs_tol=tolerance):
        log.error('Recorded {} secs and track is set to {} secs at spotify'.format(real_duration_sec, duration))
        return False
    return True
