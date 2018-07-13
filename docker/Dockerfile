FROM nvidia/cuda:8.0-runtime-ubuntu16.04

MAINTAINER Wolfgang Pernice <wolfgang.pernice@gmail.com>
MAINTAINER Sultan Kenjeyev <ksula0155@gmail.com>

ENV IS_PRODUCTION=TRUE

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
COPY requirements.txt /Ynet/
COPY .  /Ynet
WORKDIR /Ynet



# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /Ynet
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user
RUN pip3 install --no-cache-dir -r /Ynet/requirements.txt


# Set the default command to train
CMD ["python3", "train.py"]