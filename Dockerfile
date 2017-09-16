FROM python:2.7-slim
MAINTAINER Shane Canon <scanon@lbl.gov>


ADD requirements.txt /tmp/
RUN \
   pip install -r /tmp/requirements.txt

ADD . /src/ 

WORKDIR /src
ENTRYPOINT [ './sdnapi.py' ]
