FROM python:3.7.7-buster

RUN pip install flask
RUN pip install mysql-connector-python==8.0.18

COPY webserver.py /usr/bin/dtd/
COPY static /usr/bin/dtd/static
COPY config.json /usr/bin/dtd/

COPY run.sh /usr/bin/dtd
RUN chmod +x /usr/bin/dtd/run.sh


WORKDIR /usr/bin/dtd
ENTRYPOINT ./run.sh
