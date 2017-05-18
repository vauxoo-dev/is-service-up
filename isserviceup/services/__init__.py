from isserviceup.config import config
import importlib
import inspect
import os
import re
from isserviceup.services.models.service import Service
from isserviceup.services.models.multiple import MultipleService
import sys
current_module = sys.modules[__name__]


def load_services():
    pysearchre = re.compile('.py$', re.IGNORECASE)
    pluginfiles = [x for x in os.listdir(os.path.dirname(__file__))
                   if pysearchre.search(x)]
    plugins = map(lambda fp: '.' + os.path.splitext(fp)[0], pluginfiles)
    modules = []
    for plugin in plugins:
        if not plugin.startswith('.__'):
            modules.append(importlib.import_module(
                plugin, package=current_module.__name__))
    ignore = [Service, MultipleService]
    multiple = [service for service in (config.SERVICES or [])
                if ':' in service]
    services = {}
    for module in modules:
        for item_name in dir(module):
            item = getattr(module, item_name)
            if (inspect.isclass(item) and issubclass(item, Service)
                    and item not in ignore):
                service_id = item.__name__
                if (issubclass(item, MultipleService)
                        and config.SERVICES is not None):
                    for service in multiple:
                        if not service.startswith(service_id):
                            continue
                        service_split = service.split(':')
                        service_args = service_split[1:]
                        new_service_id = service_args[0]
                        if new_service_id in services:
                            raise Exception('Found multiple services with '
                                            'the name "{}"'.format(
                                                new_service_id))
                        services[new_service_id] = item(*service_args)
                else:
                    if ((config.SERVICES is not None
                            and service_id not in config.SERVICES)
                            or not isinstance(item.name, str)):
                        continue
                    if item.name in services:
                        raise Exception('Found multiple service with '
                                        'the name "{}"'.format(item.name))
                    services[service_id] = item()
    return services


SERVICES = load_services()

if __name__ == '__main__':
    print(SERVICES)
