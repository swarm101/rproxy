FROM alpine:3.14.0

RUN apk update && apk add nginx certbot-nginx docker-py py3-jinja2 curl

ADD rootfs /

RUN rm -rf /etc/nginx /etc/letsencrypt; \
	ln -s /data/etc/nginx/ /etc/; \
	ln -s /data/etc/rproxy/ /etc/; \
	ln -s /data/etc/letsencrypt/ /etc/; \
        mkdir -p /upgrade/; \
        cp -R /data/* /upgrade/; \
	pip install /src && rm -rf /src

VOLUME [ "/data/" ]

HEALTHCHECK CMD curl -f http://localhost/ || exit 1

CMD [ "rproxy" ]
