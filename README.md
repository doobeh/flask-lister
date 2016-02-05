Flask File Lister
-----------------

This is just a simple project you can copy and modify to create a simple HTTP auth
website that serves a directory of files.

The quick guide below shows how to get it operational on Ubuntu 14.04 running
the nginx web-server and gunicorn as the wsgi handler.


Quick Start
===========

First clone the repo to your server.

    git clone https://github.com/doobeh/flask-lister.git /var/www/files.example.com

Next edit the `config.py` file to match your basic users and point to the shared location
where you store the files you wish to share.

Next we need to create a virtualenv and set up our required packages

    cd /var/www/files.example.com
    virtualenv .venv
    . .venv/bin/activate
    pip install -r requirements.txt

Next up, lets create an upstart script, so the flask application gets automatically
run when the server restarts.

    sudo nano /etc/init/lister.conf

And the contents:

    description "Gunicorn application server running flask-lister"

    start on runlevel [2345]
    stop on runlevel [!2345]

    respawn
    setuid you
    setgid www-data

    env PATH=/var/www/files.example.com/.venv/bin
    chdir /var/www/files.example.com
    exec gunicorn --workers 3 --bind unix:flask-lister.sock -m 007 wsgi

Finally, we just need to create the nginx configuration, I like creating them
as `.conf` files-- but if you prefer the `sites-available` / `sites-enabled`
process, go for it.

    sudo nano /etc/nginx/conf.d/files.example.com.conf

And the contents:

    server {
        listen 80;
        server_name files.example.com;

        location / {
            include proxy_params;
            proxy_pass http://unix:/var/www/files.example.com/flask-lister.sock;
        }
    }

Lets now just fire up the wsgi app:  `sudo service lister start` and restart nginx
to pay attention to the new setup: `sudo service nginx restart`.

