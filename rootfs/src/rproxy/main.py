import logging
import threading
import time

import requests

import rproxy
import rproxy.docker
import rproxy.nginx

logging.basicConfig(level=logging.INFO)

RPROXY_NAMESPACE = "io.github.swarm101.rproxy"
RPROXY_UPSTREAM = "io.github.swarm101.rproxy.upstream"
RPROXY_DOMAINS = "io.github.swarm101.rproxy.domains"
DELAY = 5

threads = []

def service_include(service):
    # check my labels!
    rproxy_service = False
    for label in service["labels"]:
        if label.startswith(RPROXY_NAMESPACE):
            rproxy_service = True
            continue

    # there are nothing for me
    if not rproxy_service:
        return

    # validate domains
    domains = service["labels"].get(RPROXY_DOMAINS, None)
    if not domains:
        logging.error("update {name} without domains label!".format(
            **service))
        return

    domains = domains.split(" ")

    service["domains"] = []
    try:
        for domain in domains:
            scheme, location = rproxy.urlparse(domain)
            service["domains"].append({
                "scheme": scheme, 
                "location": location})
    except AssertionError as e:
        logging.error("update {name} invalid domain {domain}, should be just scheme://location".format(
            **service, domain=domain))
        return

    # validate upstream
    upstream = service["labels"].get(RPROXY_UPSTREAM, None)
    if not upstream:
        logging.error("update {name} with upstream label!".format(
            **service))
        return

    service["upstream"] = upstream.format(**service)

    # wait service be reachable
    time.sleep(DELAY)
    while service["configure"]:
        try:
            res = requests.get(service["upstream"])
            break
        except requests.exceptions.URLRequired:
            loggin.error(
                "can't configure {name}, upstream is not a URL ({upstream})".format(
                **service))
            return
        except requests.exceptions.MissingSchema:
            loggin.error(
                "can't configure {name}, upstream is missing schema ({upstream})".format(
                **service))
            return
        except requests.exceptions.InvalidURL:
            loggin.error(
                "can't configure {name}, upstream is invalid ({upstream})".format(
                **service))
            return
        except Exception as e:
            logging.warn(
                "can't configure {name}, {upstream} is unavailable, retrying in {delay} seconds".format(
                **service, delay=DELAY))
        time.sleep(DELAY)

    if not service["configure"]:
        logging.info("this configure {name}, was stopped, bye!".format(**service))
        return

    rproxy.nginx.include(service)

def service_exclude(service):
    time.sleep(DELAY)

    if not service["configure"]:
        loggin.info("this exclusion {name}, was stopped, bye!".format(**service))
        return

    rproxy.nginx.exclude(service)

def service_controller(service, routine):
    # stop already running setup
    for thread in list(threads):
        if service["id"] == thread.service["id"]:
            thread.service["configure"] = False
            thread.join()
            threads.remove(thread)

    # prepare this service
    service["configure"] = True

    # create thread and associate service
    thread = threading.Thread(target=routine, args=(service,))
    thread.service = service

    # add to running threads
    threads.append(thread)
    thread.start()

def event_normalize(event):
    return {
        "id": event["Actor"]["ID"],
        "name": event["Actor"]["Attributes"]["name"]}

def service_info(docker, event):
    service = docker.api.inspect_service(event["id"])
    return service["Spec"]["Labels"]

def service_create(docker, event):
    event = event_normalize(event)
    event["labels"] = service_info(docker, event)
    service_controller(event, service_include)

def service_update(docker, event):
    event = event_normalize(event)
    event["labels"] = service_info(docker, event)
    service_controller(event, service_include)

def service_remove(docker, event):
    event = event_normalize(event)
    service_controller(event, service_exclude)

def main():
    rproxy.nginx.start()
    rproxy.docker.watch(
        service_create=service_create,
        service_update=service_update,
        service_remove=service_remove)

main()
