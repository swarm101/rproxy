
{% for server in servers %}

{% if server.scheme == "https" %}
server {
    listen                443 ssl;
    server_name           {{server.server_name}};
    
    include               /etc/letsencrypt/options-ssl-nginx.conf;

    ssl_certificate       /etc/letsencrypt/live/{{server.server_name}}/fullchain.pem;
    ssl_certificate_key   /etc/letsencrypt/live/{{server.server_name}}/privkey.pem;
    ssl_dhparam           /etc/letsencrypt/ssl-dhparams.pem;
    
    location / {
        {% if server.headers %}
            {% for key, value in server.headers.items() %}
        proxy_set_header  "{{key}}" "{{value}}";
            {% endfor %}
        {% endif %}
        proxy_pass        {{server.proxy_pass}};
    }
}

{% else %}
server {
    listen                80;
    server_name           {{server.server_name}};

    {% if server.proxy_pass %}
    location / {
        {% if server.headers %}
            {% for key, value in server.headers.items() %}
        proxy_set_header  "{{key}}" "{{value}}";
            {% endfor %}
        {% endif %}
        proxy_pass        {{server.proxy_pass}};
    }
    
    {% else %}
    if ($host = {{server.server_name}}) {
        return            301 https://$host$request_uri;
    }

    return                404;
	{% endif %}
}
{% endif %}

{% endfor %}
