#!/bin/bash

uservar=$(whoami)

# update server
sudo apt -q update
sudo apt -q upgrade -y

# install all necessary packages
sudo apt -q install git python3 python3-pip python3-bs4 python3-flask postgresql postgresql-contrib -y

# clone github repo
sudo git clone https://github.com/Trackyr/Trackyr.git /home/$uservar/Trackyr
sudo chown -R $uservar:$uservar /home/$uservar/Trackyr/

# install pips
sudo pip3 -q install -r ~/Trackyr/src/requirements.txt

# give main.py executable permissions
sudo chmod +x /home/$uservar/Trackyr/src/main.py

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

# create systemd service for flask server
sudo touch /etc/systemd/system/trackyr.service
sudo chmod a+w /etc/systemd/system/trackyr.service

sudo cat >/etc/systemd/system/trackyr.service <<EOL
[Unit]
Description=Trackyr web server

[Install]
WantedBy=multi-user.target

[Service]
User=$uservar
WorkingDirectory=/home/$uservar/Trackyr/src
ExecStart=$(which gunicorn) -b 0.0.0.0:5000 -w 3 run:app
TimeoutSec=600
Restart=on-failure
RuntimeDirectoryMode=755
EOL

sudo systemctl daemon-reload
sudo systemctl enable trackyr.service
sudo systemctl start trackyr.service