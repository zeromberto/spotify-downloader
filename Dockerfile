FROM rb-dtr.de.bosch.com/had/osd4

LABEL maintainer="Thomas Reinhardt <thomas.reinhardt3@de.bosch.com>"

ENV NGINX_VERSION release-1.11.3

# Install nginx with required ssl dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	    nginx \
		ca-certificates \
		libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clean nginx configs
RUN rm -rf /etc/nginx/sites-available/* && rm -rf /etc/nginx/sites-enabled/*

# Copy config
COPY ./nginx.conf /etc/nginx/nginx.conf

CMD ["nginx"]



FROM rb-dtr.de.bosch.com/had/nginx

RUN mkdir -p /app/run && mkdir -p /app/log && chmod -R 777 /app/log

RUN apt-get update \
	&& apt-get install -y \
        supervisor \
        python \
        python-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install uwsgi==2.0.12

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



#FROM python:3
#
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        ffmpeg \
#    && rm -rf /var/lib/apt/lists/*
#
#WORKDIR /usr/src/app
#COPY .. .
#RUN pip install -U --no-cache-dir -r requirements.txt
#
#ENTRYPOINT ["/bin/bash"]
#CMD ["./run.sh"]

FROM ubuntu:xenial

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        pulseaudio \
        socat \
        alsa-utils \
        ffmpeg \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --home-dir /home/pulseaudio pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
&& chown -R pulseaudio:pulseaudio /home/pulseaudio

USER pulseaudio

RUN pulseaudio -D --exit-idle-time=-1 # Start the pulseaudio server \
#    pacmd load-module module-virtual-sink sink_name=v1 # Load the virtual sink and set it as default \
#    pacmd set-default-sink v1 \
#    pacmd set-default-source v1.monitor # set the monitor of v1 sink to be the default source
