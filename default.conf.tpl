events {
    worker_connections 1024;
}

server {
        listen 80;
        server_name modirnaab.ir modirnaab.ir;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }

        location /static/ {
           alias /app/static/;
        }

        location /media/ {
             alias /app/media/;
        }

    }

