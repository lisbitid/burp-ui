# -*- coding: utf8 -*-
"""
.. module:: burpui.misc.auth.interface
    :platform: Unix
    :synopsis: Burp-UI authentication interface.

.. moduleauthor:: Ziirish <hi+burpui@ziirish.me>

"""
from flask_login import UserMixin
from abc import ABCMeta, abstractmethod
import logging


class BUIloader:
    logger = logging.getLogger('burp-ui')


class BUIhandler:
    """The :class:`burpui.misc.auth.interface.BUIhandler` class maintains a list
    of ``Burp-UI`` users.

    :param app: Instance of the app we are running in
    :type app: :class:`burpui.server.BUIServer`
    """
    __metaclass__ = ABCMeta

    priority = 0

    name = None

    add_user = False
    del_user = False
    change_password = False

    def __init__(self, app=None):
        """Constructor"""
        pass  # pragma: no cover

    @abstractmethod
    def user(self, name=None):
        """The :func:`burpui.misc.auth.interface.BUIhandler.user` function
        returns the :class:`flask_login:flask_login.UserMixin` object
        corresponding to the given user name.

        :param name: Name of the user
        :type name: str

        :returns: The corresponding user object
        """
        return None  # pragma: no cover

    @property
    def loader(self):
        return None


class BUIuser(UserMixin):
    """The :class:`burpui.misc.auth.interface.BUIuser` class extends the
    :class:`flask_login:flask_login.UserMixin` class.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def login(self, passwd=None):
        """The :func:`burpui.misc.auth.interface.BUIuser.login` function
        checks if the profided username and password match.

        :param passwd: Password
        :type passwd: str

        :returns: True if the name and password match, otherwise False
        """
        return False  # pragma: no cover

    @property
    def is_active(self):
        """
        :returns: True if user is active, otherwise False
        """
        return self.active

    @property
    def is_authenticated(self):
        """
        :returns: True if a user is authenticated, otherwise False
        """
        return self.authenticated
