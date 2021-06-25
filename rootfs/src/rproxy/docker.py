import docker

client = docker.from_env()

def ignore(*args):
    pass

def watch(**kwargs):
    for service in client.services.list():
        event = {"Actor": {"ID": service.id, "Attributes": {"name": service.name}}}
        func = kwargs.get("service_update", ignore)
        func(client, event)
        
    for event in client.events(decode=True):
        func = kwargs.get("{Type}_{Action}".format(**event), ignore)
        func(client, event)
