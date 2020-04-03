FROM python:3.7.7-buster

RUN pip install mysql-connector-python==8.0.18

COPY typogenerator.py /usr/bin/dtd/

COPY run.sh /usr/bin/dtd/
RUN chmod +x /usr/bin/dtd/run.sh

COPY /config.json /usr/bin/dtd

WORKDIR /usr/bin/dtd
ENTRYPOINT ./run.sh
