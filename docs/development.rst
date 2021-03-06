Development
===========

If you wish to use the latest and yet unstable version
(eg. `master <https://git.ziirish.me/ziirish/burp-ui/tree/master>`__),
you can install it using ``pip`` too, but I would recommend you to use a
``virtualenv``.

To do so, run the following commands:

::

    mkdir /opt/bui-venv
    pip install virtualenv
    virtualenv /opt/bui-venv
    source /opt/bui-venv/bin/activate
    pip install --upgrade https://burpui.ziirish.me/builds/burp-ui.dev.tar.gz


You can uninstall/disable this `Burp-UI`_ setup by typing ``deactivate`` and
removing the ``/opt/bui-venv`` directory.


Hacking
=======

For those of you who would like to hack on the project, I have split out the
repository to keep a copy of all the external dependencies (JS and CSS) in a git
submodule.

In order to run local debugging, you need to retrieve this git submodule.

To do so, run the following commands:

::

    git clone https://git.ziirish.me/ziirish/burp-ui.git
    cd burp-ui
    git submodule update --init


.. _Burp-UI: https://git.ziirish.me/ziirish/burp-ui
