FROM ubuntu:xenial
#FROM debian:jessie

LABEL maintainer john-fistikis@red-planet.com

# Create a group and user

# SECURITY matters ?
# Why loose precious time !

# RUN addgroup -S appVLABgroup && adduser -S appVLABuser -G appVLABgroup

# Tell docker that all future commands should run as the "appVLABuser" user
# USER appVLABuser 

# home directory
# WORKDIR /appVLABuser

# root is the home directory
WORKDIR /root

# set up System-Tools 
# -------------------
# Install from a package manager because it takes so long to build.

RUN apt-get update && apt-get install -y \    
    build-essential \
    curl \
    git \
    libcurl4-openssl-dev \
    libmemcached-dev \
    libncurses5-dev \ 
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    pkg-config \
    pypy
    wget \
#    python-dev
    zliblg-dev

# Setup variables
ENV PROVISIONING /provisioning

ARG CELERY_USER=developer

# Check for mandatory build arguments
RUN : "$(CELERY_USER:?$CELERY_USER build argument needs to be set and non-empty.)"

ENV HOME /home/$CELERY_HOME
ENV PATH='$HOME/.pyenv/bin:$PATH'

# Copy and run setup scripts
WORKDIR $PROVISIONING
copy dcoker/scripts/install-couchbase.sh .

# RUN git clone -b ${CLONE_TAG} --depth 1 https://github.com/mvimplis2013/port_scanner.git . && \
#    pip install --upgrade pip && \
#    cd python && for req in $(cat requirements.txt) pydot; pip install $req; done && \
#    cd .. 


