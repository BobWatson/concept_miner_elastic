# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.194.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] Uncomment this section to install additional OS packages.

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends poppler-utils build-essential libpoppler-cpp-dev pkg-config python3-dev gettext-base

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.

# COPY build /tmp/build
# RUN cd /tmp/build && pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt \
#    && rm -rf /tmp/build

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g @angular/cli" 2>&1

RUN adduser --gecos "" --disabled-password concept_miner && \
    usermod -aG sudo concept_miner && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    mkdir -p /concept_miner && \
    chown -R concept_miner /concept_miner && \
    chown -R concept_miner /home/concept_miner/.cache

USER concept_miner

ENTRYPOINT [ "sh", "/concept_miner/run.sh"]