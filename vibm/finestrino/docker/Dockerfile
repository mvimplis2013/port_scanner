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
# RUN apt-get update && apt-get install -y \
#    build-essential \
#    git

