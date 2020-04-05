#!/bin/bash

uservar=$(whoami)

# update server
sudo apt update
sudo apt upgrade -y

# install all necessary packages
sudo apt install git python3 python3-pip python3-flask postgresql postgresql-contrib -y

# clone github repo
sudo git clone https://github.com/Trackyr/Trackyr.git /home/$uservar/Trackyr
sudo chown -R $uservar:$uservar /home/$uservar/Trackyr/

# install pips
sudo pip3 install -r ~/Trackyr/src/requirements.txt

# prepare config file for postgresql
sudo mkdir /etc/trackyr/ && sudo touch /etc/trackyr/config.json

sudo chmod a+w /etc/trackyr/config.json
sudo cat >/etc/trackyr/config.json <<EOL
{
        "SECRET_KEY": "b7f08f13e1be469b48813eff3359c9900d04d09951769c5aa97ef7f4c00c6229",
        "POSTGRES_URL": "127.0.0.1:5432",
        "POSTGRES_USER": "$uservar",
        "POSTGRES_PW": "CHANGEME",
        "POSTGRES_DB": "trackyr"
}
EOL

# setup postgresql
## Whatever you select to be your password for this user, update POSTGRES_PW in /etc/trackyr/config.json
sudo -u postgres createuser -P -s -e $uservar
sudo -u $uservar createdb trackyr

# if you need to connect to the database, use the following command:
# psql -U trackyrsu -d trackyr

# build database
cd /home/$uservar/Trackyr/src
export FLASK_APP=run.py
flask db init
flask db migrate
flask db upgrade

flask run --host=0.0.0.0
