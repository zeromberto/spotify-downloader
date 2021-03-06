import datetime
import os
import re
import subprocess
import time
from math import isclose

from core.const import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ffmpeg_debug = True if os.getenv('FFMPEG_DEBUG') else False


def record(file_name, track_name, stop_recording_handler):
    log.info('Recording {} to {}'.format(track_name, file_name))
    record_process = None
    try:
        fnull = open(os.devnull, 'w')
        record_process = subprocess.Popen(
            ['ffmpeg', '-f', 'pulse', '-i', 'default', '-b:a', '320k', '-ar', '48000', '-f', 'mp3', file_name],
            stdout=fnull, stderr=subprocess.STDOUT)
        log.debug('started recording')
        timeout = time.time() + 13
        while time.time() < timeout:
            time.sleep(0.2)
        if stop_recording_handler():
            raise RuntimeError('Playing did not start!')
        while not stop_recording_handler():
            time.sleep(0.05)
        time.sleep(5)
        record_process.terminate()
        log.debug('finished recording')
    except Exception as e:
        log.error(str(e))
    finally:
        if record_process:
            record_process.kill()
    log.info('Finished recording of {}'.format(track_name))


def get_recorded_length(file_name, method=1):
    ffmpeg_get_mediafile_length = ['ffmpeg', '-i', file_name, '-f', 'null', '-']
    output = subprocess.Popen(ffmpeg_get_mediafile_length,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT).stdout.read()
    if method == 1:
        real_duration, millis = re.findall(r'(?<=Duration: )(.*?)(?=,)', str(output))[0].split('.')
    else:
        real_duration, millis = re.findall(r'(?<=time=)(.*?)(?= )', str(output))[0].split('.')
    real_duration = time.strptime(real_duration, '%H:%M:%S')
    real_duration_sec = datetime.timedelta(hours=real_duration.tm_hour,
                                           minutes=real_duration.tm_min,
                                           seconds=real_duration.tm_sec).total_seconds()
    real_duration_sec = real_duration_sec + int(millis) / 100
    log.debug('Recorded {} secs'.format(real_duration_sec))
    return real_duration_sec


def cut_recording(file_name, spotify_duration):
    fnull = open(os.devnull, 'w')
    log.debug('Cutting off start silence')
    copy_name = file_name.replace('.mp3', '.copy.mp3')
    ffmpeg_silence_remove_cmd = ['ffmpeg',
                                 '-i', file_name,
                                 '-af', 'silenceremove=start_periods=1:start_threshold=0:detection=peak',
                                 '-b:a', '320k',
                                 '-ar', '48000',
                                 '-f', 'mp3',
                                 copy_name]
    if not ffmpeg_debug:
        subprocess.Popen(ffmpeg_silence_remove_cmd, stdout=fnull, stderr=subprocess.STDOUT).wait()
    else:
        output = subprocess.Popen(ffmpeg_silence_remove_cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT).stdout.read()
        log.debug(output)
    get_recorded_length(copy_name)
    os.remove(file_name)
    log.debug('Setting track length')
    ffmpeg_cut_length_cmd = ['ffmpeg',
                             '-i', copy_name,
                             '-ss', '0',
                             '-t', str(spotify_duration),
                             '-b:a', '320k',
                             '-ar', '48000',
                             '-f', 'mp3',
                             file_name]
    if not ffmpeg_debug:
        subprocess.Popen(ffmpeg_cut_length_cmd, stdout=fnull, stderr=subprocess.STDOUT).wait()
    else:
        output = subprocess.Popen(ffmpeg_cut_length_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read()
        log.debug(output)
    os.remove(copy_name)
    return get_recorded_length(file_name)


def verify_length(file_name, spotify_duration, play_duration, tolerance=3.0):
    if not isclose(play_duration, spotify_duration, abs_tol=tolerance):
        log.error('Played {} secs and track is set to {} secs at spotify'.format(play_duration, spotify_duration))
        return False

    try:
        real_duration_sec = get_recorded_length(file_name)
    except Exception as e:
        log.error(str(e))
        return False

    if real_duration_sec < play_duration:
        log.error('Recorded ({} secs) less than played ({} secs)'.format(real_duration_sec, play_duration))
        return False

    try:
        real_duration_sec = cut_recording(file_name, spotify_duration)
    except Exception as e:
        log.error(str(e))
        return False

    if not isclose(real_duration_sec, spotify_duration, abs_tol=tolerance):
        log.error('Recorded {} secs and track is set to {} secs at spotify'.format(real_duration_sec, spotify_duration))
        log.error('FFMPEG "Duration" reports {} secs and "time" reports {}'.format(
            get_recorded_length(file_name, 1), get_recorded_length(file_name, 2)))
        return False
    return True
