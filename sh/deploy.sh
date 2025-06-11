#!/bin/bash

cd TASTY

git pull;

SRC=/work/TASTY/ai
DEST=/$HOME/deploy

rm -rf $DEST
mkdir -p $DEST
cp -r $SRC $DEST

cd $DEST/ai

source .venv/bin/activate

streamlit run app.py