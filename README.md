# vpf-devcontainer

A [Devcontainer](https://code.visualstudio.com/docs/remote/containers)-ready template repository for NVIDIA's [Video Processing Framework](https://github.com/NVIDIA/VideoProcessingFramework)

All you need to do is create a new repo based on this template (or clone it), download the [Nvidia Video Codec SDK](https://developer.nvidia.com/nvidia-video-codec-sdk/download) into `CodecSDK/` and use the VS Code command palette to `Build and open in container`. When the container finishes building, you can hit F5 to run the `decoder.py` example or begin your own development from there!

See the video below as an example.

https://user-images.githubusercontent.com/605680/127966728-6b620fd5-0e9f-4630-ae5e-804b9d49a87c.mp4

Tested on Ubuntu, with [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script), [Visual Studio Code](https://code.visualstudio.com/docs/setup/linux) and the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension pack installed. YMMV on other platforms, including WSL.
