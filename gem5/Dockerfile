FROM ubuntu:bionic as base
ARG MAX_THREAD

COPY requirements.txt /opt/requirements.txt
WORKDIR /opt/gem5
RUN apt-get update
RUN apt-get -y install python2.7 python-pip git

RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1

RUN git clone https://github.com/gem5/gem5 "."
RUN git checkout 8c8a2f12f2f8b419723e7af8e3851033c41b7b51
RUN pip install -r "/opt/requirements.txt"

FROM base as depend
ARG MAX_THREAD
RUN apt-get -y install build-essential swig zlib1g zlib1g-dev libprotobuf-dev protobuf-compiler libprotoc-dev libgoogle-perftools-dev libboost-all-dev libhdf5-serial-dev m4 libcapstone-dev libpng-dev libelf-dev pkg-config

FROM depend as gem5
ARG MAX_THREAD

RUN scons build/X86/gem5.opt -j "${MAX_THREAD}"