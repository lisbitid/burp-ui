Introduction
============

`Burp-UI`_ is a web-based interface for `Burp`_. It's purpose is to give you a
*nice* way to monitor your backups with some dashboards, but you will also have
the ability to download files from backups and to configure your burp-server.

The project also provides a full documented `API <api.html>`_ so that you can
develop any front-end you like on top of it. The core will take care of the
communication with the burp server(s) for you.

.. note::
    Although the `Burp`_'s author and I exchange a lot, our products are totally
    distinct. So I would like people to understand some issues might be related
    to `Burp-UI`_, but some other might be related to `Burp`_ and I may not be
    able to help you in the later case.
    There is a dedicated mailing-list for `Burp`_ related issues. You can find
    details `here <http://burp.grke.org/contact.html>`_


Compatibility
-------------

+----------------------------+-------+-------+
|   Burp version \ Backend   |   1   |   2   |
+============================+=======+=======+
|         < 1.3.48           |       |       |
+----------------------------+-------+-------+
|     1.3.48 => 1.4.40       |   X   |       |
+----------------------------+-------+-------+
|     2.0.0 => 2.0.16        |       |       |
+----------------------------+-------+-------+
| 2.0.18 => 2.0.X protocol 1 |       |   X   |
+----------------------------+-------+-------+
| 2.0.18 => 2.0.X protocol 2 |       |   X*  |
+----------------------------+-------+-------+

\* The protocol 2 is in heavy development Burp side so the support in
`Burp-UI`_ is best effort and all features (such as server-initiated
restoration) are not available.


Known Issues
------------

Because it's an Open Source project, people are free (and encouraged) to open
issues in the `bug-tracker <https://git.ziirish.me/ziirish/burp-ui/issues>`_.
You will also find there the current opened issues.


There are also a few issues unrelated to the code itself:

1. SSH issue

People that would like to clone the repository over SSH will face an
authentication failure even if they added a valid SSH key in their user
settings.
The reason is I only have *one* public IP address so I must use port
redirections to have multiple SSH instances running.
To fix the issue, you should configure your SSH client by adding the following
lines in your ``~/.ssh/config`` file:

::

   Host git.ziirish.me
      Port 2222


.. _Burp: http://burp.grke.org/
.. _Burp-UI: https://git.ziirish.me/ziirish/burp-ui
