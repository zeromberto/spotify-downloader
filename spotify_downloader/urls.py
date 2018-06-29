from django.conf.urls import url, include


urlpatterns = [
    url(r'^spotify-player/', include('spotify_downloader_app.urls')),
]
