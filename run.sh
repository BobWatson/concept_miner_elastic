#!/usr/bin/env sh

export PATH=/home/concept_miner/.local/bin:$PATH
cd /concept_miner/app

if ! [ "${PRODIGY_KEY}" = "" ]
then
    mkdir /tmp/build
    envsubst < ../build/requirements.txt > /tmp/build/requirements.txt
    pip3 --disable-pip-version-check install -r /tmp/build/requirements.txt
else
    "Fail"
fi

if [ "${DEBUG}" = "true" ]
then
    envsubst < ../build/requirements-dev.txt > /tmp/build/requirements-dev.txt
    pip3 --disable-pip-version-check install -r /tmp/build/requirements-dev.txt
    sleep infinity
else
    /usr/local/bin/python ./app.py
fi
