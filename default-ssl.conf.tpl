server {
        listen 80;

        server_name localhost;

        location / {
            proxy_pass http://app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/static/;
        }

        location /media/ {
            alias /app/media/;
        }
    }

    server {
        listen 443 ssl;
        server_name modirnaab.ir www.modirnaab.ir;

# slow connections timeout
    # client_body_timeout 5s;
    # client_header_timeout 5s;

    # rate limiting
    # limit_req zone=mylimit burst=20 delay=20;
    # limit_req_status 429;

        # Let's Encrypt parameters

        ssl_session_cache shared:le_nginx_SSL:10m;
        ssl_session_timeout 1440m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;
        ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384";
        ssl_dhparam /vol/proxy/ssl-dhparams.pem;

        ssl_certificate /etc/letsencrypt/live/modirnaab.ir/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/modirnaab.ir/privkey.pem;


        # Secruity headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
        add_header Content-Security-Policy "default-src 'self'; img-src * data:; font-src 'self' data:; frame-src 'self' https://www.google.com/; connect-src 'self' ;style-src 'self' https://cdn.jsdelivr.net ;script-src 'self' https://cdn.jsdelivr.net ; object-src 'self' ;frame-ancestors 'self'; form-action 'self'; base-uri 'self';";
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options nosniff;
        add_header Referrer-Policy "strict-origin";
        add_header Permissions-Policy "geolocation=(),midi=(),sync-xhr=(),microphone=(),camera=(),magnetometer=(),gyroscope=(),fullscreen=(self),payment=()";
        add_header Set-Cookie "Path=/; HttpOnly; Secure;  SameSite=strict;";
        add_header Cache-Control "private, no-cache, no-store, must-revalidate, max-age=0" always;

        location / {
            proxy_pass http://app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /app/static/;
        }

        location /media/ {
            alias /app/media/;
        }
    }
}
