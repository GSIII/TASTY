#!/bin/bash

git pull;

SRC=/work/TASTY/ai
DEST=/$HOME/deploy

rm -rf $DEST
mkdir -p $DEST
cp -r $SRC $DEST

cd $DEST/ai

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
