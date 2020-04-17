#!/bin/bash
USERVAR=$(whoami)
USERPASS="trackyrpass"
TRACKYR_GIT_PATH="https://github.com/Trackyr/Trackyr.git"
TRACKYR_LOCAL_PATH="/etc/Trackyr"
TRACKYR_CONFIG_PATH="/etc/trackyr-config.json"
PRIVATE_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1')

GREEN='\033[0;32m'
ORANGE='\033[;33m'
RED='\033[0;31m'
NC='\033[0m'

# incase user is using this script for updating instead of installing, cd to home to make sure they are not in TRACKYR_LOCAL_PATH.
cd ~

echo "                                                                                                                                       "
echo "#######################################################################################################################################"
echo "#                                                          TRACKYR INSTALLER                                                          #"
echo "#                                                  https://github.com/Trackyr/Trackyr                                                 #"
echo "#    A self-hostable open sourced scraper of online classifieds. Customize your sources and your notification agents to search the    #"
echo "#                                      website(s) you want, and get notified the way(s) you want!                                     #"
echo "#                                                                                                                                     #"
echo "#   This script has been designed to be a single execution for a complete setup. If you would like to check which packages are being  #"
echo "#     automatically installed, which paths are being used, etc. then please use CTRL+C to stop the script now. You can review the     #"
echo "#                     contents at https://raw.githubusercontent.com/Trackyr/Trackyr/master/src/scripts/install.sh                     #"
echo "#######################################################################################################################################"
echo "                                                                                                                                       "

sleep 15

printf "\n\n"

# update server
printf "${GREEN}[> START <]   Updating and Upgrading System Packages${NC}\n"
sleep 1

sudo apt -q update
sudo apt -q upgrade -y

sleep 1
printf "${RED}[> END <]   Updating and Upgrading System Packages${NC}\n"



sleep 2.5
echo ""



# install all necessary packages
printf "${GREEN}[> START <]   Installing necessary packages${NC}\n"
sleep 1

sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt -q install git python3.7 python3-pip python3-bs4 python3-flask postgresql postgresql-contrib -y

sleep 1
printf "${RED}[> END <]   Installing necessary packages${NC}\n"



sleep 2.5
echo ""



# clone github repo
printf "${GREEN}[> START <]   Cloning GitHub Repo (Trackyr/Trackyr) to $TRACKYR_LOCAL_PATH${NC}\n"
sleep 1

if [[ -d "$TRACKYR_LOCAL_PATH" ]]; then
    printf "${ORANGE}[> INFO <] $TRACKYR_LOCAL_PATH already exists, deleting the contents so that we can clone into it.${NC}\n"
    sudo rm -rf "$TRACKYR_LOCAL_PATH"
fi
sudo git clone -q $TRACKYR_GIT_PATH $TRACKYR_LOCAL_PATH
sudo chown -R $USERVAR:$USERVAR $TRACKYR_LOCAL_PATH

sudo touch $TRACKYR_LOCAL_PATH/src/ads.json
sudo chmod a+w $TRACKYR_LOCAL_PATH/src/ads.json
echo '{}' >> $TRACKYR_LOCAL_PATH/src/ads.json

sleep 1
printf "${RED}[> END <]   Cloning GitHub Repo (Trackyr/Trackyr) to $TRACKYR_LOCAL_PATH${NC}\n"



sleep 2.5
echo ""



# install pips
printf "${GREEN}[> START <]   Installing Python packages${NC}\n"
sleep 1

python3.7 -m pip -q install -r $TRACKYR_LOCAL_PATH/src/requirements.txt

sleep 1
printf "${RED}[> END <]   Installing Python packages${NC}\n"



sleep 2.5
echo ""



printf "${GREEN}[> START <]   Preparing crontab and other permissions${NC}\n"
sleep 1

# give main.py executable permissions
sudo chmod +x $TRACKYR_LOCAL_PATH/src/main.py

# create blank crontab
crontab -l > mycron
echo "" >> mycron
crontab mycron
rm mycron

sleep 1
printf "${RED}[> END <]   Preparing crontab and other permissions${NC}\n"



sleep 2.5
echo ""



# prepare config file for postgresql
printf "${GREEN}[> START <]   Setup database${NC}\n"
sleep 1

sudo touch $TRACKYR_CONFIG_PATH
sudo chmod a+w $TRACKYR_CONFIG_PATH
sudo cat >$TRACKYR_CONFIG_PATH <<EOL
{
        "SECRET_KEY": "b7f08f13e1be469b48813eff3359c9900d04d09951769c5aa97ef7f4c00c6229",
        "POSTGRES_URL": "127.0.0.1:5432",
        "POSTGRES_USER": "$USERVAR",
        "POSTGRES_PW": "$USERPASS",
        "POSTGRES_DB": "trackyr"
}
EOL

sudo touch $TRACKYR_LOCAL_PATH/src/trackyr/config.py
sudo chmod a+w $TRACKYR_LOCAL_PATH/src/trackyr/config.py
sudo cat >$TRACKYR_LOCAL_PATH/src/trackyr/config.py <<EOL
import os
import json

with open('$TRACKYR_CONFIG_PATH') as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('SECRET_KEY')

    POSTGRES_URL = config.get('POSTGRES_URL')
    POSTGRES_USER = config.get('POSTGRES_USER')
    POSTGRES_PW = config.get('POSTGRES_PW')
    POSTGRES_DB = config.get('POSTGRES_DB')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}"
EOL

# setup postgresql
## Whatever you select to be your password for this user, update POSTGRES_PW in /etc/trackyr-config.json
doesPostUserExist=$(psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$USERVAR'")
if [[ doesPostUserExist -lt 1 ]] ; then
    printf "${ORANGE}[> INFO <] $USERVAR doesn't exist, creating the user.${NC}\n"
    sudo -u postgres createuser -s -E $USERVAR
    psql postgres -tAc "ALTER USER \"${USERVAR}\" WITH ENCRYPTED PASSWORD '${USERPASS}'"
    sudo rm ~/.psql_history
fi
doesTrackyrDatabaseExist=$(psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname='trackyr'")
if [[ doesTrackyrDatabaseExist -lt 1 ]] ; then
    printf "${ORANGE}[> INFO <] trackyr database doesn't exist, creating the table.${NC}\n"
    sudo -u $USERVAR createdb trackyr
fi

# build database
cd $TRACKYR_LOCAL_PATH/src
export FLASK_APP=run.py
python3.7 -m flask db init
python3.7 -m flask db migrate
python3.7 -m flask db upgrade

sleep 1
printf "${RED}[> END <]   Setup database${NC}\n"



sleep 2.5
echo ""



# create systemd service for flask server
printf "${GREEN}[> START <]   Creating systemd service for WebUI${NC}\n"
sleep 1

sudo touch /etc/systemd/system/trackyr.service
sudo chmod a+w /etc/systemd/system/trackyr.service

sudo cat >/etc/systemd/system/trackyr.service <<EOL
[Unit]
Description=Trackyr web server

[Install]
WantedBy=multi-user.target

[Service]
User=$USERVAR
WorkingDirectory=$TRACKYR_LOCAL_PATH/src
ExecStart=/home/$USERVAR/.local/bin/gunicorn -b 0.0.0.0:5000 -w 3 run:app
TimeoutSec=600
Restart=on-failure
RuntimeDirectoryMode=755
EOL

sudo systemctl daemon-reload
sudo systemctl enable trackyr.service
sudo systemctl start trackyr.service

sleep 1
printf "${RED}[> END <]   Creating systemd service for WebUI${NC}\n"



sleep 1
echo ""



printf "${ORANGE}[> INFO <]   You can access the WebUI at $PRIVATE_IP:5000${NC}\n"