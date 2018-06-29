import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


logger = logging.getLogger("basic_logger")


def spotify_player(request, *args, **kwargs):
    template = loader.get_template('player.html')
    return HttpResponse(template.render({}, request))


def spotify_player_login(request, *args, **kwargs):
    return HttpResponseRedirect('https://accounts.spotify.com/authorize?client_id=0c23e8b7d41e4cda88ca631e50df0d1e&redirect_uri=http:%2F%2Flocalhost:8000%2Fspotify-player%2Fplay%2F&scope=user-read-private%20user-read-email%20streaming&response_type=token&state=123')