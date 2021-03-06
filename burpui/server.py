# -*- coding: utf8 -*-
"""
.. module:: burpui.server
    :platform: Unix
    :synopsis: Burp-UI server module.

.. moduleauthor:: Ziirish <hi+burpui@ziirish.me>

"""
import os
import sys
import logging
import traceback

from .misc.auth.handler import UserAuthHandler
from .utils import BUIConfig
from datetime import timedelta

from flask import Flask


G_PORT = 5000
G_BIND = u'::'
G_REFRESH = 180
G_LIVEREFRESH = 5
G_SSL = False
G_STANDALONE = True
G_SSLCERT = u''
G_SSLKEY = u''
G_VERSION = 1
G_AUTH = [u'basic']
G_ACL = u'none'
G_STORAGE = u''
G_REDIS = u''
G_SCOOKIE = False
G_APPSECRET = u'random'
G_COOKIETIME = 14
G_PREFIX = u''


class BUIServer(Flask):
    """
    The :class:`burpui.server.BUIServer` class provides the ``Burp-UI`` server.
    """
    gunicorn = False

    defaults = {
        'Global': {
            'port': G_PORT,
            'bind': G_BIND,
            'ssl': G_SSL,
            'standalone': G_STANDALONE,
            'sslcert': G_SSLCERT,
            'sslkey': G_SSLKEY,
            'version': G_VERSION,
            'auth': G_AUTH,
            'acl': G_ACL,
            'prefix': G_PREFIX,
        },
        'UI': {
            'refresh': G_REFRESH,
            'liverefresh': G_LIVEREFRESH,
        },
        'Security': {
            'scookie': G_SCOOKIE,
            'appsecret': G_APPSECRET,
            'cookietime': G_COOKIETIME,
        },
        'Production': {
            'storage': G_STORAGE,
            'redis': G_REDIS,
        }
    }

    def __init__(self):
        """The :class:`burpui.server.BUIServer` class provides the ``Burp-UI``
        server.

        :param app: The Flask application to launch
        """
        self.init = False
        # We cannot override the Flask's logger so we use our own
        self.builogger = logging.getLogger('burp-ui')
        self.builogger.disabled = True
        super(BUIServer, self).__init__('burpui')

    def enable_logger(self, enable=True):
        """Enable or disable the logger"""
        self.builogger.disabled = not enable

    @property
    def logger(self):
        return self.builogger

    def setup(self, conf=None):
        """The :func:`burpui.server.BUIServer.setup` functions is used to setup
        the whole server by parsing the configuration file and loading the
        different backends.

        :param conf: Path to a configuration file
        :type conf: str
        """
        self.sslcontext = None
        if not conf:
            conf = self.config['CFG']

        if not conf:
            raise IOError('No configuration file found')

        # Raise exception if errors are encountered during parsing
        self.conf = BUIConfig(conf, True, self.defaults)
        self.conf.default_section('Global')

        self.port = self.conf.safe_get(
            'port',
            'integer'
        )
        self.bind = self.conf.safe_get('bind')
        self.vers = self.conf.safe_get(
            'version',
            'integer'
        )
        self.ssl = self.conf.safe_get(
            'ssl',
            'boolean'
        )
        self.standalone = self.conf.safe_get(
            'standalone',
            'boolean'
        )
        self.sslcert = self.conf.safe_get(
            'sslcert'
        )
        self.sslkey = self.conf.safe_get(
            'sslkey'
        )
        self.prefix = self.conf.safe_get(
            'prefix'
        )
        if self.prefix and not self.prefix.startswith('/'):
            if self.prefix.lower() != 'none':
                self.logger.warning("'prefix' must start with a '/'!")
            self.prefix = ''

        self.auth = self.conf.safe_get(
            'auth',
            'string_lower_list'
        )
        if self.auth and 'none' not in self.auth:
            try:
                self.uhandler = UserAuthHandler(self)
            except Exception as e:
                self.logger.critical(
                    'Import Exception, module \'{0}\': {1}'.format(
                        self.auth,
                        str(e)
                    )
                )
                raise e
            self.acl_engine = self.conf.safe_get(
                'acl'
            )
        else:
            self.config['LOGIN_DISABLED'] = True
            # No login => no ACL
            self.acl_engine = 'none'
            self.auth = 'none'

        if self.acl_engine and self.acl_engine.lower() != 'none':
            try:
                # Try to load submodules from our current environment
                # first
                sys.path.insert(
                    0,
                    os.path.dirname(os.path.abspath(__file__))
                )
                mod = __import__(
                    'burpui.misc.acl.{0}'.format(
                        self.acl_engine.lower()
                    ),
                    fromlist=['ACLloader']
                )
                ACLloader = mod.ACLloader
                self.acl_handler = ACLloader(self)
                # for development purpose only
                from .misc.acl.interface import BUIacl
                self.acl = BUIacl
                self.acl = self.acl_handler.acl
            except Exception as e:
                self.logger.critical(
                    'Import Exception, module \'{0}\': {1}'.format(
                        self.acl_engine,
                        str(e)
                    )
                )
                raise e
        else:
            self.acl_handler = False
            self.acl = False

        # UI options
        self.config['REFRESH'] = self.conf.safe_get(
            'refresh',
            'integer',
            'UI'
        )
        self.config['LIVEREFRESH'] = self.conf.safe_get(
            'liverefresh',
            'integer',
            'UI'
        )

        # Production options
        self.storage = self.conf.safe_get(
            'storage',
            section='Production'
        )
        self.redis = self.conf.safe_get(
            'redis',
            section='Production'
        )

        # Security options
        self.scookie = self.conf.safe_get(
            'scookie',
            'boolean',
            section='Security'
        )
        self.config['SECRET_KEY'] = self.conf.safe_get(
            'appsecret',
            section='Security'
        )
        days = self.conf.safe_get('cookietime', 'integer', section='Security') \
            or 0
        self.config['REMEMBER_COOKIE_DURATION'] = \
            self.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
                days=days
        )

        self.config['STANDALONE'] = self.standalone

        self.logger.info('burp version: {}'.format(self.vers))
        self.logger.info('listen port: {}'.format(self.port))
        self.logger.info('bind addr: {}'.format(self.bind))
        self.logger.info('use ssl: {}'.format(self.ssl))
        self.logger.info('standalone: {}'.format(self.standalone))
        self.logger.info('sslcert: {}'.format(self.sslcert))
        self.logger.info('sslkey: {}'.format(self.sslkey))
        self.logger.info('prefix: {}'.format(self.prefix))
        self.logger.info('secure cookie: {}'.format(self.scookie))
        self.logger.info(
            'cookietime: {}'.format(self.config['REMEMBER_COOKIE_DURATION'])
        )
        self.logger.info('refresh: {}'.format(self.config['REFRESH']))
        self.logger.info('liverefresh: {}'.format(self.config['LIVEREFRESH']))
        self.logger.info('auth: {}'.format(self.auth))
        self.logger.info('acl: {}'.format(self.acl_engine))

        if self.standalone:
            module = 'burpui.misc.backend.burp{0}'.format(self.vers)
        else:
            module = 'burpui.misc.backend.multi'

        # This is used for development purpose only
        from .misc.backend.burp1 import Burp as BurpGeneric
        self.cli = BurpGeneric(dummy=True)
        try:
            # Try to load submodules from our current environment
            # first
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            mod = __import__(module, fromlist=['Burp'])
            Client = mod.Burp
            self.cli = Client(self, conf=self.conf)
        except Exception as e:
            traceback.print_exc()
            self.logger.critical(
                'Failed loading backend for Burp version {0}: {1}'.format(
                    self.vers,
                    str(e)
                )
            )
            sys.exit(2)

        self.init = True

    def manual_run(self):
        """The :func:`burpui.server.BUIServer.manual_run` functions is used to
        actually launch the ``Burp-UI`` server.
        """
        if not self.init:
            self.setup()

        if self.ssl:
            self.sslcontext = (self.sslcert, self.sslkey)

        if self.sslcontext:
            self.config['SSL'] = True
            self.run(
                host=self.bind,
                port=self.port,
                debug=self.config['DEBUG'],
                ssl_context=self.sslcontext
            )
        else:
            self.run(host=self.bind, port=self.port, debug=self.config['DEBUG'])
