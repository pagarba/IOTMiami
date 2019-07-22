#!/bin/bash

#REPO="https://github.com/pagarba/IOTMaimi"
REPO="https://github.com/dustinengle/IOTMaimi"

echo "Updating system..." && \
sudo apt update -y && \
sudp apt install -y curl git python python-pip vim && \
echo "Updating system...Done!" && \

echo "Cloning source code..." && \
git clone $REPO && \
echo "Cloning source code...Done!" && \

echo "Installing packages..." && \
cd IOTMiami && \
pip install -r requirements.txt && \
echo "Installing packages...Done!" && \

echo "Setup complete!"