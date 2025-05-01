# For more information, see https://aka.ms/vscode-remote/devcontainer.json

# ...existing code...
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# ffmpegインストール
RUN apt-get update && apt-get install -y ffmpeg

# uv（Pythonパッケージマネージャ）インストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# bash-completionの設定(uvの設定)
RUN echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# ...existing code...