import requests
from enum import Enum
from decouple import config
from isserviceup.notifiers.notifier import Notifier


class CachetStatus(Enum):
    ok = 1
    minor = 2
    major = 3
    critical = 4

    @staticmethod
    def get_cachet_status(status):
        from isserviceup.services.models.service import Status
        status_map = {
            Status.ok: CachetStatus.ok,
            Status.maintenance: CachetStatus.minor,
            Status.minor: CachetStatus.minor,
            Status.major: CachetStatus.major,
            Status.critical: CachetStatus.critical,
            Status.unavailable: CachetStatus.critical,
        }
        status = status and Status[status]
        return status_map.get(status, CachetStatus.critical)

    @staticmethod
    def get_status_name(status):
        status_name = {
            CachetStatus.ok: 'OK',
            CachetStatus.minor: 'Minor',
            CachetStatus.major: 'Major',
            CachetStatus.critical: 'Critical',
        }
        return status_name.get(status, 'Undefined')

    @staticmethod
    def get_incident_status(status):
        if status == CachetStatus.ok:
            return 4  # Solved
        else:
            return 1  # Investigating


class Cachet(Notifier):
    """Notifies to the Cachet status page components, about the state of their
    corresponding services.

    :param cachet_url: The URL for the Cachet status page.
        If empty, will get it from config('CACHET_URL').
    :type cachet: str
    :param cachet_token: The Cachet API Token.
        If empty, will get it from config('CACHET_TOKEN').
    :type cachet_token: str
    :param cachet_components: Which components in Cachet are going to be
        notified. Is a dictionary with each key being the service class, and
        its value, the Cachet component id. If empty, will get it from
        config('CACHET_COMPONENTS'), and it has to be a comma separated string
        with each service class, a colon, and the component id. (For example,
        CACHET_COMPONENTS=Docker:1,Github:4)
    :type cachet_components: dict
    """

    def __init__(self, cachet_url="", cachet_token="",
                 cachet_components=None):
        self.cachet_url = cachet_url or config('CACHET_URL', default=None)
        self.cachet_token = (cachet_token or
                             config('CACHET_TOKEN', default=None))
        self.cachet_components = (cachet_components or
                                  config('CACHET_COMPONENTS', default=None,
                                         cast=self._components_to_dict))

    def _components_to_dict(self, components=None):
        try:
            return dict([[side.strip() for side in component.split(":")]
                         for component in components.split(",")])
        except ValueError as error:
            print("Value error: {msg}".format(msg=error.message))
            return {}

    def _get_component_name(self, service):
        return service.id

    def _get_component_id(self, service):
        component = self._get_component_name(service)
        return self.cachet_components.get(component)

    def _get_component_url(self, service):
        url = "{base_url}/api/v1/incidents".format(
            base_url=self.cachet_url.strip("/")
        )
        return url

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Cachet-Token': self.cachet_token,
        }

    def _build_payload(self, service, old_status, new_status):
        payload = {
            'name': 'Status changed',
            'message': 'Service **{service}** changed from *{old}* to *{new}*'.format(
                service=service.name,
                old=CachetStatus.get_status_name(old_status),
                new=CachetStatus.get_status_name(new_status)
            ),
            'status': CachetStatus.get_incident_status(new_status),
            'visible': 1,
            'component_id': self._get_component_id(service),
            'component_status': new_status.value,
            'notify': True
        }
        return payload

    def _is_valid(self, service):
        return (
            self.cachet_url and self.cachet_token and self.cachet_components
            and self._get_component_id(service)
        )

    def notify(self, service, old_status, new_status):
        old_status = CachetStatus.get_cachet_status(old_status)
        new_status = CachetStatus.get_cachet_status(new_status)
        if self._is_valid(service) and old_status != new_status:
            url = self._get_component_url(service)
            headers = self._get_headers()
            payload = self._build_payload(service, old_status, new_status)
            print("Notifying {} with {}".format(url, payload))
            requests.post(url, json=payload, headers=headers)
