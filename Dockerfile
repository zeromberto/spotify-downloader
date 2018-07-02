FROM ubuntu:xenial

RUN apt-get update \
    && apt-get install -y \
        software-properties-common \
        locales \
        wget \
    && add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-get update \
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
        \
        python3.6 \
        python3.6-dev \
        python3-pip \
        firefox \
        \
        libsasl2-dev \
        libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

RUN useradd --create-home --home-dir /home/pulseaudio pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
	&& chown -R pulseaudio:pulseaudio /home/pulseaudio

COPY client.conf /etc/pulse/client.conf
COPY daemon.conf /etc/pulse/daemon.conf

# Clean nginx configs
RUN rm -rf /etc/nginx/sites-available/* && rm -rf /etc/nginx/sites-enabled/*
# Copy config
COPY ./nginx.conf /etc/nginx/nginx.conf
RUN mkdir -p /app/run && mkdir -p /app/log && chmod -R 777 /app/log
RUN python3.6 -m pip install --upgrade pip
RUN python3.6 -m pip install uwsgi


# Copy config files
COPY supervisor.conf /app/run/supervisord.conf
# UWSGI configuration
ENV UWSGI_MASTER=1 UWSGI_WORKERS=3 UWSGI_THREADS=3
# User config
RUN useradd -ms /bin/bash -G www-data app-user && \
	usermod -a -G app-user www-data && \
	chown -R app-user /app && \
	chmod -R 777 /app && \
	chown -R www-data /var/lib/nginx
CMD ["supervisord", "-n", "-c", "/app/run/supervisord.conf", "-u", "root"]
WORKDIR /app


ENV DJANGO_SETTINGS_MODULE=spotify_downloader.settings
COPY ./requirements.txt ./
RUN python3.6 -m pip install -r requirements.txt
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz \
	&& tar -xvzf geckodriver-v0.20.0-linux64.tar.gz \
	&& chmod +x geckodriver \
	&& mv geckodriver /usr/local/bin/ \
	&& rm geckodriver-v0.20.0-linux64.tar.gz

# Nginx configuration
COPY ./site.conf /etc/nginx/sites-enabled/
# App configuration
ENV APP_NAME=spotify_downloader
COPY ./spotify_downloader ./spotify_downloader
COPY ./spotify_downloader_app ./spotify_downloader_app
COPY ./core ./core
COPY ./bash ./bash
COPY ./spotdl.py ./spotdl.py
COPY ./my.default ./my.default

