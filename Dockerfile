FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Need git, because requirements.txt includes a repository
# gcc and mysql library are required for the mysqlclient package
RUN apt-get -y update && \
    apt-get -y install gcc && \
    apt-get -y install git && \
    apt-get -y install default-libmysqlclient-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"
ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/src/
RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

CMD  ["gunicorn", "--config", "/usr/src/app/gunicorn_config.py", "ensembl.production.gifts.app.main:app"]
