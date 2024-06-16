FROM python:3.9

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

COPY ./mysql/init.sql /docker-entrypoint-initdb.d/

RUN mkdir -p /var/uploads && \
    chown www-data:www-data /var/uploads && \
    chmod 660 /var/uploads

RUN mkdir -p /var/uploads/user1 \
    mkdir -p /var/uploads/admin

CMD ["python", "app.py"]
