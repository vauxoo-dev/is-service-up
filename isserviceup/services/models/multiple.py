from decouple import config
from isserviceup.services.models.service import Service, Status


class MultipleService(Service):
    """Service that can be added to the SERVICES list multiple times, giving
    it an alias to differentiate between them.

    When extending this class, you should only override the 'prefix' property,
    and the 'get_status' function.

    To add a MultipleService to the config file you must concatenate an alias
    separated with a colon from the service name.

    Lets say you have a service extending this class called: MyMultiService.

    :Example:

        SERVICES=MyMultiService:MyUniqueAlias,MyMultipleService:AnotherAlias

    After that you can set its particular configuration options adding the
    prefix and concatenating the alias (uppercased) as a suffix. Something like
    this:

        # In the config file (.env)
        {PREFIX}_{OPTION_NAME}_{SERVICEALIAS}=Value

    By default, you can set a name, service url, and icon. The names for these
    options are:

        SERVICE_NAME: The service name you want to see on the website
        URL: The service URL to check its status
        ICON: The icon that'll be displayed with the name

    Assuming the service class has a prefix of 'MMS', and the services were
    added like shown above, then to access this options, you should do:

        # MyUniqueAliasConfiguration
        MMS_SERVICE_NAME_MYUNIQUEALIAS=My service
        MMS_URL_MYUNIQUEALIAS=https://theurlformyservice.com/
        MMS_ICON_MYUNIQUEALIAS=/images/icons/myicon.png

    And do the same for the service with the alias AnotherAlias and all the
    other you might have added.

    Note: you can add the icons to the '/static/images/icons/' directory and
    run 'npm run build' to easily add them to your services. You can also set
    an external url if the icon is hosted somewhere else.

    To access the options from inside the service, you can use the 'config'
    function, passing it the option name, and optionally: a default value and
    a cast function. Like this:

        # Inside any function inside the service
        the_service_name = self.config('SERVICE_NAME')

    This will automatically concatenate the alias and prefix for the current
    service and return the correct value (if it was correctly set in the config
    file .env).
    """

    def __init__(self, alias=""):
        super(MultipleService, self).__init__()
        self.alias = alias

    def config(self, option, default="", cast=None):
        """Returns the option for the current service, concatenating the prefix
        and the alias when looking for it in the config file (.env).

        :param option: The option name (should be uppercase).
        :param default: A default value if nothing was set.
        :param cast: A cast function (everything on the config file is a str,
            so if you need this to return another type, for example an integer,
            send the needed cast function, for example int).
        """
        return config(
            '{option}_{alias}'.format(option=option, alias=self.alias.upper()),
            default=default, cast=cast or str
        )

    @property
    def id(self):
        return self.alias

    @property
    def prefix(self):
        raise NotImplemented()

    @property
    def name(self):
        return self.config('{prefix}_SERVICE_NAME'.format(prefix=self.prefix))

    @property
    def status_url(self):
        return self.config('{prefix}_URL'.format(prefix=self.prefix))

    @property
    def icon_url(self):
        return self.config('{prefix}_ICON'.format(prefix=self.prefix))
