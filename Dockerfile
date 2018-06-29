FROM ubuntu:xenial

RUN apt-get update \
    && apt-get install -y \
        pulseaudio \
        socat \
        alsa-utils \
        ffmpeg \
        \
        nginx \
		ca-certificates \
		libssl-dev \
		\
		supervisor \
        python3 \
        python3-pip \
        \
        libsasl2-dev \
        libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*


RUN useradd --create-home --home-dir /home/pulseaudio pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
&& chown -R pulseaudio:pulseaudio /home/pulseaudio
USER pulseaudio
RUN pulseaudio -D --exit-idle-time=-1 # Start the pulseaudio server
#    pacmd load-module module-virtual-sink sink_name=v1 # Load the virtual sink and set it as default \
#    pacmd set-default-sink v1 \
#    pacmd set-default-source v1.monitor # set the monitor of v1 sink to be the default source
USER root


# Clean nginx configs
RUN rm -rf /etc/nginx/sites-available/* && rm -rf /etc/nginx/sites-enabled/*
# Copy config
COPY ./nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /app/run && mkdir -p /app/log && chmod -R 777 /app/log
RUN pip3 install --upgrade pip
RUN pip3 install uwsgi


# Copy config files
COPY supervisor.conf /app/run/supervisord.conf
# UWSGI configuration
ENV UWSGI_MASTER=1 UWSGI_WORKERS=3 UWSGI_THREADS=3
# User config
RUN useradd -ms /bin/bash -G www-data app-user && \
	usermod -a -G app-user www-data && \
	chown -R app-user /app && \
	chown -R www-data /var/lib/nginx
CMD ["supervisord", "-n", "-c", "/app/run/supervisord.conf", "-u", "root"]
WORKDIR /app


ENV DJANGO_SETTINGS_MODULE=spotify_downloader.settings
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt
# Nginx configuration
COPY ./site.conf /etc/nginx/sites-enabled/
# App configuration
ENV APP_NAME=spotify_downloader
COPY ./spotify_downloader ./spotify_downloader
COPY ./spotify_downloader_app ./spotify_downloader_app

