FROM nvidia/cuda:8.0-runtime-ubuntu16.04

MAINTAINER Wolfgang Pernice <wolfgang.pernice@gmail.com>
MAINTAINER Sultan Kenjeyev <ksula0155@gmail.com>


# Install some basic utilities
RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y \
    curl \
    ca-certificates \
    python3-pip \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    python3.6 \
 && rm -rf /var/lib/apt/lists/*

# Create a working directoryCOPY requirements.txt /PyWeaver/
COPY ./requirements.txt /Ynet/requirements.txt
RUN python3.6 -m pip install -r /Ynet/requirements.txt

COPY .  /Ynet
WORKDIR /Ynet

ENV PRODUCTION=TRUE
ENV CONFIG_FILE_PATH="./Ynet.meta.yaml"

# Set the default command to train
CMD ["python3.6", "train.py"]