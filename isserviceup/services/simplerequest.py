import requests
from isserviceup.services.models.service import Status
from isserviceup.services.models.multiple import MultipleService


class SimpleRequest(MultipleService):
    """Service that checks if a URL is active and responding with a 200 OK.

    You must give this an alias when adding it to the service list. Also,
    you must set the SR_SERVICE_NAME_{ALIAS}, SR_URL_{ALIAS}, and
    SR_ICON_{ALIAS}. For more information on this, read the MultipleService
    class documentation.
    """

    prefix = 'SR'

    def _check_http(self):
        request = requests.get(self.status_url)
        return request.ok

    def get_status(self):
        if self._check_http():
            return Status.ok
        return Status.critical
