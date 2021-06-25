server {
    listen           80;
    server_name      {{server_name}};
    
    location / {
        proxy_pass   {{proxy_pass}};
    }
}
