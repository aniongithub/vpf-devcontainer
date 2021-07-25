#!/bin/bash

set -e
set -u

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

NV_CODEC_SDK_ZIP_FILENAME="Video_Codec_SDK_*.zip"
NV_CODEC_SDK_ZIP_PATH="${SCRIPT_DIR}/CodecSDK/${NV_CODEC_SDK_ZIP_FILENAME}"
if [ ! -f ${NV_CODEC_SDK_ZIP_PATH} ]; then
    echo "Please download version ${NV_CODEC_SDK_VERSION} of the NVIDIA Video Codec SDK for developers from https://developer.nvidia.com/nvidia-video-codec-sdk/download to ${SCRIPT_DIR}/CodecSDK first!"
    exit 1
fi