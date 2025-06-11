#!/bin/bash

git pull;

SRC=/work/TASTY/ai
DEST=/$HOME/deploy

rm -rf $DEST
mkdir -p $DEST
cp -r $SRC $DEST

cd $DEST/ai

pids=$(ps -ef | grep streamlit | grep -v grep | awk '{print $2}')
if [ -n "$pids" ]; then
    echo "Killing existing Streamlit processes: $pids"
    kill -9 $pids
fi

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
