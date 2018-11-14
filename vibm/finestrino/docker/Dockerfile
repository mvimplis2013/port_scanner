#
# Dockerfile for VLAB-External-Monitor
#

FROM debian:jessie
MAINTAINER vibm <mvimblis@gmail.com>

ENV VLAB_EXT_VER 0.0.1

ENV VLAB_EXT_URL https://github.com/mvimplis2013/vlab_ext-${VLAB_EXT_VER}.tar.gz

ENV VLAB_EXT_SHA xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ENV VLAB_EXT_FILE vlab_ext.tar.gz
ENV VLAB_EXT_TEMP vlab-ext
ENV VLAB_EXT_DEPS build-essential curl

# set -x ... Print commands and their arguments as executed 
#     -e ... Exit immediately if a command exits with a non-zero status. 
RUN set -xe \
    && apt-get update \
    && apt-get install -y ${VLAB_EXT_DEPS} \
    && mkdir ${VLAB_EXT_TEMP} \
    && cd ${VLAB_EXT_TEMP} \
    && curl -sSL ${VLAB_EXT_URL} -o ${VLAB_EXT_FILE} \
    && echo "${VLAB_EXT_SHA} *{VLAB_EXT_FILE}" | shasum -c \
    && tar xzf ${VLAB_EXT_FILE} --strip 1 \
    && pip install -r requirements.txt
