FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
        software-properties-common \
        locales \
        wget \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y \
        pulseaudio \
        socat \
        alsa-utils \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y \
        supervisor \
        \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://apt.mopidy.com/mopidy.gpg | apt-key add - \
    && wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/stretch.list \
    && apt-get update \
    && apt-get install -y \
        mopidy \
        mopidy-spotify \
    && rm -rf /var/lib/apt/lists/*

# Only here for slugify
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en

RUN useradd --create-home --home-dir /home/pulseaudio pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
	&& chown -R pulseaudio:pulseaudio /home/pulseaudio

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Copy config files
COPY supervisor.conf /app/run/supervisord.conf
COPY client.conf /etc/pulse/client.conf
COPY daemon.conf /etc/pulse/daemon.conf
COPY mopidy.conf /var/lib/mopidy/.config/mopidy/mopidy.conf

RUN mkdir -p /app/run && mkdir -p /app/log && chmod -R 777 /app/log && chmod 777 /app
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install setuptools

WORKDIR /app

COPY ./requirements.txt ./
RUN python3 -m pip install -r requirements.txt

RUN usermod -G audio,sudo mopidy \
    && chmod -R 777 /var/lib/mopidy \
    && chmod go+rwx -R /var/lib/mopidy
ENV HOME=/home/pulseaudio
#RUN chmod -R 777 /root/ /home/pulseaudio

COPY ./bash ./bash
COPY ./mopidy_json_client ./mopidy_json_client
COPY ./core ./core
COPY ./spotdl.py ./spotdl.py
COPY ./run.sh ./run.sh

CMD ["supervisord", "-n", "-c", "/app/run/supervisord.conf", "-u", "root"]
