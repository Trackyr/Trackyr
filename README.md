<h1 align="center">
  <br>
  Trackyr
  <br>
</h1>

<h4 align="center">An aggregator for second-hand and classified ad sites.</h4>

<p align="center">
  :star: Star us on GitHub! || :eye: Watch for updates!
</p>

<p align="center">
  <a href="https://www.codacy.com/gh/Trackyr/Trackyr?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Trackyr/Trackyr&amp;utm_campaign=Badge_Grade">
    <img src="https://api.codacy.com/project/badge/Grade/2abccb4b868f41c792ca213c647ca003" alt="Codacy">
  </a>
  <a href="https://discord.com/invite/zCcH2z?utm_source=Discord%20Widget&utm_medium=Connect">
    <img src="https://img.shields.io/discord/689477994750017558?label=Discord" alt="Discord">
  </a>
  <a href="https://github.com/Trackyr/Trackyr/issues">
    <img src="https://img.shields.io/github/issues/Trackyr/Trackyr?label=Issues" alt="Issues">
  </a>
  <a href="https://github.com/Trackyr/Trackyr/pulls">
    <img src="https://img.shields.io/github/issues-pr/Trackyr/Trackyr?label=Pull%20Requests" alt="Pull Requests">
  </a>
</p>
  
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
