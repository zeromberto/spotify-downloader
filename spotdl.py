#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import platform
import pprint
import sys
import time
import urllib.request
from random import shuffle

import spotipy
from slugify import slugify

from core import const
from core import handle
from core import internals
from core import metadata
from core import player
from core import record
from core import spotify_tools
from core import youtube_tools

__version__ = '0.9.3'


def check_exists(music_file, raw_song, meta_tags):
    """ Check if the input song already exists in the given folder. """
    log.debug('Cleaning any temp files and checking '
              'if "{}" already exists'.format(music_file))
    songs = os.listdir(const.args.folder)
    for song in songs:
        if song.endswith('.temp'):
            os.remove(os.path.join(const.args.folder, song))
            continue
        # check if any song with same name is already present in the given folder
        if os.path.splitext(song)[0] == music_file:
            log.debug('Found an already existing song: "{}"'.format(song))
            if internals.is_spotify(raw_song):
                # check if the already downloaded song has correct metadata
                # if not, remove it and download again without prompt
                already_tagged = metadata.compare(os.path.join(const.args.folder, song), meta_tags)
                log.debug('Checking if it is already tagged correctly? {}', already_tagged)
                if not already_tagged:
                    os.remove(os.path.join(const.args.folder, song))
                    return False

            # log.warning('"{}" already exists'.format(song))
            log.debug('Skipping "{}"'.format(song))
            return True

            # log.warning('"{}" already exists'.format(song))
            # if const.args.overwrite == 'prompt':
            #     log.info('"{}" has already been downloaded. '
            #              'Re-download? (y/N): '.format(song))
            #     prompt = input('> ')
            #     if prompt.lower() == 'y':
            #         os.remove(os.path.join(const.args.folder, song))
            #         return False
            #     else:
            #         return True
            # elif const.args.overwrite == 'force':
            #     os.remove(os.path.join(const.args.folder, song))
            #     log.info('Overwriting "{}"'.format(song))
            #     return False
            # elif const.args.overwrite == 'skip':
            #     log.info('Skipping "{}"'.format(song))
            #     return True
    return False


def download_list(text_file):
    """ Download all songs from the list. """
    log.debug('Python version: {}'.format(sys.version))
    log.debug('Platform: {}'.format(platform.platform()))
    with open(text_file, 'r') as listed:
        lines = (listed.read()).splitlines()
    # ignore blank lines in text_file (if any)
    try:
        lines.remove('')
    except ValueError:
        pass

    shuffle(lines)
    log.info('Preparing to download {} songs from {}\n'.format(len(lines), str(text_file).rsplit('/')[-1]))
    downloaded_songs = []
    timeout = time.time() + 45 * 60

    for number, raw_song in enumerate(lines, 1):
        if time.time() > timeout:
            log.info('Playlist timeout! Stopping download of playlist.\nDownloaded {} tracks.'.format(number-1))
            return downloaded_songs

        try:
            download_single(raw_song, number=number)
        # token expires after 1 hour
        except spotipy.client.SpotifyException:
            # refresh token when it expires
            log.debug('Token expired, generating new one and authorizing')
            new_token = spotify_tools.generate_token()
            spotify_tools.spotify = spotipy.Spotify(auth=new_token)
            download_single(raw_song, number=number)
        # detect network problems
        except (urllib.request.URLError, TypeError, IOError) as e:
            lines.append(raw_song)
            # remove the downloaded song from file
            internals.trim_song(text_file)
            # and append it at the end of file
            with open(text_file, 'a') as myfile:
                myfile.write(raw_song + '\n')
            log.error(repr(e))
            log.warning('Failed to download song. Will retry after other songs\n')
            # wait 0.5 sec to avoid infinite looping
            time.sleep(0.5)
            continue

        downloaded_songs.append(raw_song)
        log.debug('Removing downloaded song from text file')
        internals.trim_song(text_file)

    log.info('Finished downloading {} songs from {}\n'.format(len(downloaded_songs), str(text_file).rsplit('/')[-1]))
    return downloaded_songs


def download_single(raw_song, number=None):
    """ Logic behind downloading a song. """
    if internals.is_youtube(raw_song):
        log.debug('Input song is a YouTube URL')
        content = youtube_tools.go_pafy(raw_song, meta_tags=None)
        raw_song = slugify(content.title).replace('-', ' ')
        meta_tags = spotify_tools.generate_metadata(raw_song)
    else:
        meta_tags = spotify_tools.generate_metadata(raw_song)

        # content = youtube_tools.go_pafy(raw_song, meta_tags)

    # if content is None:
    #     log.debug('Found no matching video')
    #     return
    #
    if const.args.download_only_metadata and meta_tags is None:
        log.info('Found no metadata. Skipping the download')
        return

    # "[number]. [artist] - [song]" if downloading from list
    # otherwise "[artist] - [song]"
    # youtube_title = youtube_tools.get_youtube_title(content, number)
    # log.info('{} ({})'.format(youtube_title, content.watchv_url))
    #
    # generate file name of the song to download
    songname = 'foo'

    if meta_tags is not None:
        refined_songname = internals.format_string(const.args.file_format,
                                                   meta_tags,
                                                   slugification=True)
        log.debug('Refining songname from "{0}" to "{1}"'.format(songname, refined_songname))
        if not refined_songname == ' - ':
            songname = refined_songname
    else:
        log.warning('Could not find metadata')
        songname = internals.sanitize_title(songname)

    if const.args.dry_run:
        log.info(songname)
        check_exists(songname, raw_song, meta_tags)
        return

    if not check_exists(songname, raw_song, meta_tags):
        # deal with file formats containing slashes to non-existent directories
        songpath = os.path.join(const.args.folder, os.path.dirname(songname))
        os.makedirs(songpath, exist_ok=True)
        file_name = os.path.join(const.args.folder, songname + const.args.output_ext)
        player.play_and_record(meta_tags['uri'], file_name, songname)
        if not record.verify_length(file_name, meta_tags['duration']):
            log.error('Duration mismatch! Deleting: {}'.format(songname))
            os.remove(file_name)
            return False
        if not const.args.no_metadata and meta_tags is not None:
            metadata.embed(file_name, meta_tags)
        return True


def main():
    const.args = handle.get_arguments()

    if const.args.version:
        print('spotdl {version}'.format(version=__version__))
        sys.exit()

    internals.filter_path(const.args.folder)
    youtube_tools.set_api_key()

    const.log = const.logzero.setup_logger(formatter=const._formatter,
                                      level=const.args.log_level)
    global log
    log = const.log
    log.debug('Python version: {}'.format(sys.version))
    log.debug('Platform: {}'.format(platform.platform()))
    log.debug(pprint.pformat(const.args.__dict__))

    try:
        if const.args.song:
            download_single(raw_song=const.args.song)
        elif const.args.list:
            download_list(text_file=const.args.list)
        elif const.args.playlist:
            spotify_tools.write_playlist(playlist_url=const.args.playlist)
        elif const.args.album:
            spotify_tools.write_album(album_url=const.args.album)
        elif const.args.username:
            spotify_tools.write_user_playlist(username=const.args.username)

        # actually we don't necessarily need this, but yeah...
        # explicit is better than implicit!
        sys.exit(0)

    except KeyboardInterrupt as e:
        log.exception(e)
        sys.exit(3)


if __name__ == '__main__':
    main()
