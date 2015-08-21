#!/bin/bash

# setting the SO
sudo apt-get update
sudo apt-get -y install apache2
sudo apt-get -y install unzip

PK=$(curl http://metadata/computeMetadata/v1/instance/attributes/package -H "X-Google-Metadata-Request: True")

#Configuring server web
cd /var/www/
sudo rm index.html

#Configuring mobile site
sudo wget https://storage.googleapis.com/genx/$PK.zip
sudo unzip $PK.zip
sudo rm $PK.zip



