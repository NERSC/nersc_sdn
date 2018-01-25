#
# Just the pieces to run the service.
# Munged and mongo would need to be running an properly passed in.
#
FROM python:2.7-slim
MAINTAINER Shane Canon <scanon@lbl.gov>

RUN apt-get -y update && apt-get -y install munge

ADD requirements.txt /tmp/
RUN \
   pip install -r /tmp/requirements.txt

ADD . /src/ 
RUN \
   cd /src/ && python ./setup.py install

WORKDIR /src
CMD ["/usr/local/bin/gunicorn", "-b", "0.0.0.0:5000", "nersc_sdn.sdnapi:application"]
