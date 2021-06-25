FROM alpine:3.14.0

RUN apk update && apk add nginx certbot-nginx docker-py py3-jinja2

ADD rootfs /

RUN /bin/sh -x /usr/local/bin/rproxy-setup.sh

VOLUME [ "/data/" ]

CMD [ "rproxy" ]
