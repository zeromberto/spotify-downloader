import os

from mopidy_spotify import backend, playback
from mopidy import audio, backend as models
from mopidy import __main__ as momain

from mopidy_json_client import MopidyClient

mopidy = MopidyClient()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# extensions_data = ext.load_extensions()
# mopidy_config, config_errors = config.load(BASE_DIR + '/mopidy.conf',
#                                            [d.config_schema for d in extensions_data],
#                                            [d.config_defaults for d in extensions_data],
#                                            None)


def play_and_record(filename="foo", track_uri="spotify:track:1L1dpImK36DoZPr7rxy0hJ"):
    momain.main()
    m_backend = backend.SpotifyBackend(mopidy_config, m_audio)
    m_backend.start()
    player = playback.SpotifyPlaybackProvider(audio=m_audio, backend=m_backend)
    track = models.Track(uri=track_uri)

    player.change_track(track)


play_and_record()
