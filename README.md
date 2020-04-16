<h1>:robot: Trackyr</h1>

<h2>One-Command Installation</h2>

Known to work on a fresh Ubuntu 18.04 LTS server
>$ bash <(curl -s https://raw.githubusercontent.com/Trackyr/Trackyr/master/src/scripts/install.sh)



<h2>(OPTIONAL) Manual Password Change</h2>

**This is not a requirement.**

Trackyr sets up a user in postgresql using the system user's name and a default password of "trackyrpass". This password is only used for trackyr to communicate with the database.

However, if you do not feel safe using the default password, here are a few steps to change the necessary files/database entries.

>$ sudo nano /etc/trackyr-config.json

Change the "POSTGRES_PW" to the password that you would like to use.

>$ psql postgres -tAc "ALTER USER \"$(whoami)\" WITH ENCRYPTED PASSWORD 'PASSWORD_GOES_HERE'"

It should respond "ALTER ROLE" if it went through.

Lastly, restart the service.

>$ sudo systemctl restart trackyr.service
