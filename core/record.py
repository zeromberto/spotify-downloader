import datetime
import os
import re
import subprocess
import time
from math import isclose

from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from core.const import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def verify_length(file_name, duration, tolerance=3.0):
    ffmpeg_get_mediafile_length = [
        'sh', '-c', 'ffmpeg -i "$1" 2>&1 | grep Duration',
        '_', file_name
    ]
    try:
        output = subprocess.Popen(ffmpeg_get_mediafile_length,
                                  stdout=subprocess.PIPE
                                  ).stdout.read()
        real_duration = re.findall(r'(?<=Duration: )(.*?)(?=,)', str(output))[0]
        real_duration = time.strptime(real_duration.split('.')[0], '%H:%M:%S')
        real_duration_sec = datetime.timedelta(hours=real_duration.tm_hour,
                                               minutes=real_duration.tm_min,
                                               seconds=real_duration.tm_sec).total_seconds()
        log.debug('Recorded {} secs and track is set to {} secs at spotify'.format(real_duration_sec, duration))
    except Exception as e:
        log.error(str(e))
        return False

    if not isclose(real_duration_sec, duration, abs_tol=tolerance):
        log.error('Recorded {} secs and track is set to {} secs at spotify'.format(real_duration_sec, duration))
        return False
    return True


def play_and_record(track_uri, file_name, track_name):
    options = Options()
    options.add_argument('--headless')
    log.debug('Firefox starting')
    driver = webdriver.Firefox(firefox_options=options, firefox_profile=BASE_DIR + '/my.default')
    log.debug('Firefox ready')
    driver.implicitly_wait(10)
    try:
        driver.get('%s%s' % ('http://localhost:8000', reverse('spotify_downloader_app:login')))
        WebDriverWait(driver, 30).until(lambda driver: driver.execute_script('return document.readyState').__eq__('complete'))
        WebDriverWait(driver, 30).until(lambda driver: driver.execute_script('return ready'))
        log.debug(driver.execute_script('return document.readyState'))
        log.debug(driver.execute_script('return ready'))
        driver.find_element_by_id('uri').send_keys(track_uri)
        driver.find_element_by_id('play').click()

        WebDriverWait(driver, 30).until(lambda driver: is_playing(driver))
        log.debug('playing')

        record(driver, file_name, track_name)
    except TimeoutError as e:
        log.error(e)
    except Exception as e:
        log.error(e)
    finally:
        log.debug('Quitting firefox')
        driver.quit()


def is_playing(driver):
    state = driver.execute_script('return player_state')
    try:
        if not state['paused']:
            return True
    except (KeyError, TypeError):
        pass
    return False


def is_paused(driver):
    state = driver.execute_script('return player_state')
    try:
        if state['paused']:
            return True
    except (KeyError, TypeError):
        pass
    return False


def record(driver, file_name, track_name):
    log.info('Recording {} to {}'.format(track_name, file_name))
    try:
        FNULL = open(os.devnull, 'w')
        record_process = subprocess.Popen(
            ['ffmpeg', '-f', 'pulse', '-i', 'default', '-b:a', '320k', '-f', 'mp3', file_name],
            stdout=FNULL, stderr=subprocess.STDOUT)
        log.debug('started recording')
        WebDriverWait(driver, 360).until(lambda driver: is_paused(driver))
        log.debug('finished')
        record_process.terminate()
    except Exception as e:
        log.error(e)
    finally:
        if record_process:
            record_process.kill()
    log.info('Finished recording of {}'.format(track_name))
