#!/bin/sh
set -e

certbot renew --test-cert --register-unsafely-without-email --agree-tos

mkdir -p /data/etc/ /data/var/lib/ /data/var/log/

mv /etc/letsencrypt /data/etc/
mv /etc/nginx /data/etc/
mv /var/lib/letsencrypt /data/var/lib/
mv /var/log/letsencrypt /data/var/log/

ln -s /data/etc/letsencrypt /etc/
ln -s /data/etc/nginx /etc/
ln -s /data/etc/rproxy /etc/
ln -s /data/var/lib/letsencrypt /var/lib/
ln -s /data/var/log/letsencrypt /var/log/

pip install /src && rm -rf /src