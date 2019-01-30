# Pull Base Image ... Tag 3.7-alpine3.8
FROM python:3.7-alpine3.8

#  version
ENV NOMADS_VERSION 1.2.3

ENV NOMADS_BASE_DIR /opt/nomads
ENV NOMADS_HOME=${NOMADS_BASE_DIR}/nomads-${NOMADS_VERSION}

ENV NOMADS_URL=https://raw.githubusercontent.com/mvimplis2013/port_scanner/master/vibm/nomads/archives
ENV NOMADS_TGZ=nomads_devel_config.tgz

# Make NOMADS folders and download project files
RUN mkdir -p ${NOMADS_HOME} \
  && cd ${NOMADS_HOME} \
  && wget ${NOMADS_URL}/${NOMADS_TGZ} -O ./${NOMADS_TGZ} \ 
  && tar -xvzf ${NOMADS_TGZ} \
  && ls -l \
  && pip install -r dev_requirements.txt \ 
  && pip freeze

#CMD ["python", "/nomads/config.py"]