FROM ubuntu:xenial

LABEL maintainer john-fistikis@red-planet.com

# Create a group and user

# Why loose precious time .... thinking about Security ?
# RUN addgroup -S appVLABgroup && adduser -S appVLABuser -G appVLABgroup

# Tell docker that all future commands should run as the "appVLABuser" user
# USER appVLABuser 

# home directory
# WORKDIR /appVLABuser

# Play with the Big guys
# root is the home directory
WORKDIR /root

# set up the system tools 
# -----------------------
# RUN apt-get update && apt-get install -y --no-install-recommends \
#    build-essential \
#    git \
#    wget \
#    curl \
#    python-dev 

# RUN git clone -b ${CLONE_TAG} --depth 1 https://github.com/mvimplis2013/port_scanner.git . && \
#    pip install --upgrade pip && \
#    cd python && for req in $(cat requirements.txt) pydot; pip install $req; done && \
#    cd .. 


