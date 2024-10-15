# Dockerfile may have following Arguments:
# tag - tag for the Base image, (e.g. 2.9.1 for tensorflow)
# branch - user repository branch to clone (default: master, another option: test)
#
# To build the image:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value .
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> .
#
# [!] Note: For the Jenkins CI/CD pipeline, input args are defined inside the
# Jenkinsfile, not here!
ARG tag=2.9.1

# Base image, e.g. tensorflow/tensorflow:2.9.1
FROM tensorflow/tensorflow:${tag}

LABEL maintainer='Carolin Leluschko'
LABEL version='0.0.1'
# Integration of DeepaaS API and litter assessment software

# What user branch to clone [!]
ARG branch=test-face-recognition
#ARG branch=main

# Install Ubuntu packages
# - gcc is needed in Pytorch images because deepaas installation might break otherwise (see docs) (it is already installed in tensorflow images)
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        git \
        curl \
        nano \
    && rm -rf /var/lib/apt/lists/*

# Update python packages
RUN python3 --version && \
    pip3 install --no-cache-dir --upgrade pip "setuptools<60.0.0" wheel

# TODO: remove setuptools version requirement when [1] is fixed
# [1]: https://github.com/pypa/setuptools/issues/3301

# Set LANG environment
ENV LANG=C.UTF-8

# Set the working directory
WORKDIR /srv

# Install rclone (needed if syncing with NextCloud for training; otherwise remove)
RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.deb && \
    dpkg -i rclone-current-linux-amd64.deb && \
    apt install -f && \
    mkdir /srv/.rclone/ && \
    touch /srv/.rclone/rclone.conf && \
    rm rclone-current-linux-amd64.deb && \
    rm -rf /var/lib/apt/lists/*

ENV RCLONE_CONFIG=/srv/.rclone/rclone.conf

# Initialization scripts
# deep-start can install JupyterLab or VSCode if requested
RUN git clone https://github.com/ai4os/deep-start /srv/.deep-start && \
    ln -s /srv/.deep-start/deep-start.sh /usr/local/bin/deep-start

# Necessary for the Jupyter Lab terminal
ENV SHELL=/bin/bash

# Install user app
RUN git clone --depth 1 -b $branch https://github.com/ai4os-hub/litter-assessment && \
     cd  litter-assessment && \
     pip3 install --no-cache-dir -e . && \
     cd ..

# Download network weights
ENV SWIFT_CONTAINER=https://share.services.ai4os.eu/index.php/s/HQmXS7mcDK82sz3/download/
ENV MODEL_TAR=models.tar.gz
ENV FACE_DETECTION_CONTAINER=https://share.services.ai4os.eu/index.php/s/amnYEs3qn8rTszS/download/
ENV FACE_DETECTION_TAR=face_detection_model.tar.gz

RUN curl --insecure -o ./litter-assessment/models/${MODEL_TAR} \
    ${SWIFT_CONTAINER}${MODEL_TAR}

RUN cd litter-assessment/models && \
     tar -xf ${MODEL_TAR}
    
RUN curl --insecure -o ./litter-assessment/models/${FACE_DETECTION_TAR} \
    ${FACE_DETECTION_CONTAINER}${FACE_DETECTION_TAR}

RUN cd litter-assessment/models && \
    tar -xf ${FACE_DETECTION_TAR}

RUN cd /srv/litter-assessment

# Open ports (deepaas, monitoring, ide)
EXPOSE 5000 6006 8888

# Launch deepaas
CMD ["deepaas-run", "--listen-ip", "0.0.0.0", "--listen-port", "5000"]
