Flask File Lister
-----------------

This project pairs Flask-AutoIndex with Flask-BasicAuth to build a simple functional
password protected file list.

Since this is BasicAuth, user names and passwords are going to be passed in cleartext
over the wire for each request. If that's important to you, follow the "Using HTTPS" guide at
the bottom to enable HTTPS for your Flask/Nginx application.


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

Using HTTPS
===========

Basic Auth does what it says on the tin, it's the bare minimum.  We can shore up
one of it's weaknesses by enabling SSL for the site.  Basic Auth still has some
weaknesses (the browser remembers it, it's sent in every request) so you can judge
but it's good for most simple cases.

So, lets first install letsencrypt and get a certificate for our `files.example.com`
domain.  We're going to be shutting down nginx for a few minutes.

    sudo git clone https://github.com/letsencrypt/letsencrypt /opt/letsencrypt
    cd /opt/letsencrypt
    sudo service nginx stop
    ./letsencrypt-auto certonly --standalone

Accept the agreement (after reading it!), fill in your email
and the files.example.com domain and any other combinations you may want to use
like `example.com` and `www.example.com`.  If everything is good it'll let you know
where it's store the files in `/etc/letsencrypt`.  Let's get our nginx server
running again!

    sudo service nginx start

Now we can alter the nginx conf file to use SSL

    sudo nano /etc/nginx/conf.d/files.example.com.conf

With the new contents:

    server {
        listen 443 ssl;

        ssl on;
        ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

        server_name files.example.com;

        location / {
            include proxy_params;
            proxy_pass http://unix:/var/www/files.example.com/flask-lister.sock;
        }
    }

    server {
        listen 80;
        server_name files.example.com;
        return 301 https://files.example.com$request_uri;
    }


All we're essentially doing is saying if someone tries to access the domain on the
unsecured port then redirect them over to the `https://` connection.

Let's Encrypt's certificates last for three months— so just remember to rerun the
command when you get close to that date. You'll need to restart nginx when you get
the new certificate (`sudo service nginx restart`).
