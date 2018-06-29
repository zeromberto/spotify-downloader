from django.conf.urls import url

from spotify_downloader_app.views import spotify_player, spotify_player_login

app_name = 'spotify_downloader_app'

urlpatterns = [
    url(r'^play/$', spotify_player, name='player'),
    url(r'^login/$', spotify_player_login, name='login'),
]
