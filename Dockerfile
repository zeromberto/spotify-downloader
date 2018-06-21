FROM python:3

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY spotify-downloader/ ./
RUN pip install -U --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "spotdl.py", "-uze.romberto"]
