FROM nvidia/cuda:11.4.0-devel-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive

# nvidia docker runtime env
ENV NVIDIA_VISIBLE_DEVICES \
        ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
        ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics,compat32,utility,video

RUN apt update &&\
    apt install -y git cmake wget unzip ffmpeg python3 virtualenv build-essential pkg-config python3-dev python3-pip \
        libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev

WORKDIR /usr/local/src
RUN git clone https://github.com/PyAV-Org/PyAV.git
RUN cd PyAV && git checkout 44195b6
RUN /bin/bash -c "cd PyAV && source scripts/activate.sh && pip install --upgrade -r tests/requirements.txt && make"
RUN cd PyAV && pip3 install .

RUN export CUDACXX=$(which nvcc)

ADD CodecSDK/Video_Codec_SDK_*.zip /tmp
RUN unzip /tmp/Video_Codec_SDK_*.zip -d /usr/local/src

ARG FIND_VIDEO_CODEC_SDK="find /usr/local/src/ -type d -name \"Video_Codec_SDK_*\" | head -1"
ARG FIND_PYTHON_VERSION="python3 -c 'import sys; print(\".\".join(map(str, sys.version_info[0:2])))'"

WORKDIR /usr/local/src/VideoProcessingFramework
RUN git clone https://github.com/NVIDIA/VideoProcessingFramework.git /usr/local/src/VideoProcessingFramework
RUN mkdir build && cd build &&\
    VIDEO_CODEC_SDK_DIR=$(eval ${FIND_VIDEO_CODEC_SDK}) &&\
    PYTHON_SHORT_VERSION=$(eval ${FIND_PYTHON_VERSION}) &&\
    LIBPYTHON_PATH="/usr/lib/x86_64-linux-gnu/libpython${PYTHON_SHORT_VERSION}.so" &&\
    echo "VIDEO_CODEC_SDK_DIR=${VIDEO_CODEC_SDK_DIR} PYTHON_SHORT_VERSION=${PYTHON_SHORT_VERSION} LIBPYTHON_PATH=${LIBPYTHON_PATH}" &&\
    cmake .. \
        -DFFMPEG_DIR:PATH="$(which ffmpeg)" \
        -DVIDEO_CODEC_SDK_DIR:PATH="${VIDEO_CODEC_SDK_DIR}" \
        -DGENERATE_PYTHON_BINDINGS:BOOL="1" \
        -DGENERATE_PYTORCH_EXTENSION:BOOL="0" \
        -DPYTHON_LIBRARY="${LIBPYTHON_PATH}" \
        -DPYTHON_EXECUTABLE="$(which python3)" .. \
        -DCMAKE_INSTALL_PREFIX:PATH="." &&\
    make -j$(nproc) && make install &&\
    cp ./bin/*.so /usr/local/lib &&\
    ldconfig

ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}"
ENV PYTHONPATH "/usr/local/lib:${PYTHONPATH}"

RUN pip3 install numpy &&\
    apt-get update &&\
    apt-get install -y python3-opencv