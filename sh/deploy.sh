#!/bin/bash

git pull;

for pid in $(ps -ef | grep streamlit | grep -v grep | awk '{print $2}'); do
    echo "Killing process $pid"
    kill -9 "$pid"
done

SRC=/work/TASTY/ai
DEST=/$HOME/deploy

rm -rf $DEST
mkdir -p $DEST
cp -r $SRC $DEST

cd $DEST/ai

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py --server.port=8501 &

