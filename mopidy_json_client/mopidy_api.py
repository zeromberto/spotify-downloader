import logging
from distutils.version import LooseVersion

logger = logging.getLogger(__name__)


class MopidyAPI(object):

    version = None
    controllers = None
    eventlist = None

    @classmethod
    def set_version(cls, version):
        assert LooseVersion(version) >= LooseVersion('1.1'), \
            'Mopidy API version %s is not supported' % version
        cls.version = version

        import mopidy_json_client.m2_2_2 as methods

        cls.controllers = methods
        cls.eventlist = methods.mopidy_eventlist


class MopidyWSController(object):
    ''' Base class of the controller wrapper classes
        It implements the function mopidy_request, which will be called by subclasses methods
    '''
    def __init__(self, request_handler):
        self._request_handler_ = request_handler

    def mopidy_request(self, method, **kwargs):
        # try:
            # args_text = ['%s=%r' % (arg, value)
            #              for arg, value in kwargs.iteritems()]
            # logger.debug('[REQUEST] %s (%s)' % (method, ', '.join(args_text)))
        # except Exception as ex:
        #     logger.exception(ex)

        return self._request_handler_(method, **kwargs)


class CoreController(MopidyWSController):
    ''' Implements ::method::describe and ::method::get_version of Mopidy Core
        It also provides ::method::send which can be used for testing
    '''
    def describe(self, **options):
        return self.mopidy_request('core.describe', **options)

    def get_version(self, **options):
        return self.mopidy_request('core.get_version', **options)

    def send(self, method, **params):
        return self.mopidy_request('core.' + method, **params)
