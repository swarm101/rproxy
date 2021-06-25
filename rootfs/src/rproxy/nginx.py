import logging
import os
import subprocess

import jinja2

NGINX_PATH = "/etc/nginx/http.d"

jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("/etc/rproxy/templates/"))

def reload():
    try:
        rc = subprocess.call(["nginx", "-s", "reload"])
        assert rc == 0, "invalid return code {rc}".format(rc=rc)
        logging.info("nginx reloded!")
        return True
    except Exception as e:
        logging.error("cannot reload nginx: {e}".format(e=e))
        return False

def start():
    try:
        rc = subprocess.call(["nginx"])
        assert rc == 0, "invalid return code {rc}".format(rc=rc)
        logging.info("nginx started!")
        return True
    except Exception as e:
        logging.error("cannot start nginx: {e}".format(e=e))
        return False

def certbot(service):
    command = [
        "certbot",
        "certonly",
        "--register-unsafely-without-email",
        "--agree-tos",
        "--nginx",
        "--keep-until-expiring",
        "-d",
        service["context"]["server_name"]]

    try:
        rc = subprocess.call(command)
        assert rc == 0, "invalid return code {rc}".format(rc=rc)
        logging.info("certbot finished!")
        return True
    except Exception as e:
        logging.error("cannot run certbot: {e}".format(e=e))
        return False

def save_config(template_name, service):
    template = jinja.get_template(template_name)
    configure = template.render(**service["context"])

    filename = "{id}.conf".format(**service)
    filename = os.path.join(NGINX_PATH, filename)

    try:
        with open(filename, "w") as f:
            f.write(configure)
        return True
    except Exception as e:
        return False

def setup_stage2(service):
    domains_http = [i for i in service["domains"] if i["scheme"] == "http"]
    domains_https = [i for i in service["domains"] if i["scheme"] == "https"]

    for domain in domains_http:
        domain["upstream"] = service["upstream"]

    for domain in domains_https:
        domain["upstream"] = service["upstream"]
        create_redirect = True
        
        for domain2 in domains_http:
            if domain["location"] == domain2["location"]:
                create_redirect = False

        if not create_redirect:
            continue

        domains_http.append({
            "location": domain["location"],
            "scheme": "http", 
            "upstream": None})

    service["domains"] = domains_http + domains_https
    
    context = {"servers": []}

    for domain in service["domains"]:
        context["servers"].append({
            "scheme": domain["scheme"],
            "server_name": domain["location"],
            "proxy_pass": domain["upstream"]})

    service["context"] = context
    save_config("stage2.tpl", service)

    if not reload():
        logging.error("stage2 reload for {name} failed!".format(
            **service))
        return

    logging.info("stage2 for {name} ok!".format(
        **service))

def setup_stage1(service):
    for domain in service["domains"]:
        if domain["scheme"] == "https":
            service["context"] = {
                "scheme": domain["scheme"],
                "server_name": domain["location"],
                "proxy_pass": service["upstream"]}

            save_config("stage1.tpl", service)
            
            if not reload():
                logging.error("stage1 reload for {location} failed".format(
                    **domain))
                return

            if not certbot(service):
                logging.error("stage1 certbot for {location} failed".format(
                    **domain))
                return

    logging.info("stage1 for {name} ok!".format(
        **service))

def include(service):
    setup_stage1(service)
    setup_stage2(service)

    logging.info("include {name} ok!".format(
        **service))

def exclude(service):
    filename = "{id}.conf".format(**service)
    filename = os.path.join(NGINX_PATH, filename)

    try:
        os.unlink(filename)
    except Exception as e:
        return False

    if not reload():
        logging.error("exclude reload for {name} failed".format(
            **service))
        return

    logging.info("exclude {name} ok!".format(
        **service))
