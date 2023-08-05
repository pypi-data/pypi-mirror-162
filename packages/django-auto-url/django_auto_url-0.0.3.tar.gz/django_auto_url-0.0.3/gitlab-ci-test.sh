#!/bin/sh
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list
apt-get update
apt-get dist-upgrade -y
apt-get install wget
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
apt-get update
apt-get install -y --force-yes google-chrome-stable unzip git curl software-properties-common
curl -sL https://deb.nodesource.com/setup_6.x | bash -
apt-get install -y nodejs

cd $CI_PROJECT_DIR
pip install -U -r requirements.txt
seleniumbase install chromedriver
pytest --headless --cov=./django_auto_url && tox && codecov