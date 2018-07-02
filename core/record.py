import os
import subprocess

from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
uri = 'spotify:track:5egCSjWOXvbIcEeVSFEBc9'


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


def play_and_record(track_uri, track_name):

    options = Options()
    # Disable proxy
    # options.set_preference('network.proxy.type', 0)
    options.add_argument('--headless')

    login_state = False
    driver = webdriver.Firefox(firefox_options=options, firefox_profile=BASE_DIR + '/my.default')
    # driver.set_window_size(1855, 1103)
    driver.implicitly_wait(10)
    try:
        if not login_state:
            driver.get('%s%s' % ('http://localhost:8000', reverse('spotify_downloader_app:login')))
        WebDriverWait(driver, 30).until(lambda driver: driver.execute_script('return document.readyState').__eq__('complete'))
        WebDriverWait(driver, 30).until(lambda driver: driver.execute_script('return ready'))
        print(driver.execute_script('return document.readyState'))
        print(driver.execute_script('return ready'))
        driver.find_element_by_id('uri').send_keys(uri)
        driver.find_element_by_id('play').click()

        WebDriverWait(driver, 30).until(lambda driver: is_playing(driver))
    #record

        print('playing')
        record_process = subprocess.Popen(['ffmpeg', '-f', 'pulse', '-i', 'default', '/data/' + track_name + '.mp3'])
        # record_process.communicate()
        # record_process = subprocess.Popen(['./bash/record.sh', '/data/test'])
        # transform_process = subprocess.Popen(['lame', '-x', '-',  'out.mp3'], stdin=record_process.stdout, stdout=subprocess.PIPE)
        # while not Path('/stop').is_file():
        #     time.sleep(2)
        print('started recording')
        WebDriverWait(driver, 360).until(lambda driver: is_paused(driver))
        print('finished')
    except TimeoutError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        print('Killing all processes')
        # transform_process.terminate()
        # record_process.terminate()
        driver.quit()


# play_and_record('', 'foo')
