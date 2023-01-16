# wreck

## INSTALLATION
Make sure that your /etc/nginx/sites-enabled/default contains:

        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
        }

        location /rpicam/ws/ {
                proxy_redirect off;
                proxy_pass http://0.0.0.0:8001;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
        }

        location /api {
                proxy_redirect off;
                proxy_pass http://0.0.0.0:8002;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
        }


And make sure that its root (for example: root /var/www/html) is pointing to wreck/html (for example, through a symlink).