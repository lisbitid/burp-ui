# -*- coding: utf8 -*-
"""
.. module:: burpui.api.clients
    :platform: Unix
    :synopsis: Burp-UI clients api module.

.. moduleauthor:: Ziirish <hi+burpui@ziirish.me>

"""
from . import api, cache_key
from .custom import fields, Resource
from ..exceptions import BUIserverException

from six import iteritems
from flask import current_app as bui

ns = api.namespace('clients', 'Clients methods')


@ns.route('/running',
          '/<server>/running',
          '/running/<client>',
          '/<server>/running/<client>',
          endpoint='running_clients')
class RunningClients(Resource):
    """The :class:`burpui.api.clients.RunningClients` resource allows you to
    retrieve a list of clients that are currently running a backup.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``serverName`` is supported when running
    in multi-agent mode.
    """
    parser = ns.parser()
    parser.add_argument('serverName', help='Which server to collect data from when in multi-agent mode')

    @ns.expect(parser)
    @ns.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
            'client': 'Client name',
        },
    )
    def get(self, client=None, server=None):
        """Returns a list of clients currently running a backup

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            [ 'client1', 'client2' ]


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :param client: Ask a specific client in order to know if it is running a backup
        :type client: str

        :returns: The *JSON* described above.
        """
        server = server or self.parser.parse_args()['serverName']
        if client:
            if bui.acl:
                if (not self.is_admin and not
                        bui.acl.is_client_allowed(self.username,
                                                  client,
                                                  server)):
                    r = []
                    return r
            if bui.cli.is_backup_running(client, server):
                r = [client]
                return r
            else:
                r = []
                return r

        r = bui.cli.is_one_backup_running(server)
        # Manage ACL
        if bui.acl and not self.is_admin:
            if isinstance(r, dict):
                new = {}
                for serv in bui.acl.servers(self.username):
                    allowed = bui.acl.clients(self.username, serv)
                    new[serv] = [x for x in r[serv] if x in allowed]
                r = new
            else:
                allowed = bui.acl.clients(self.username, server)
                r = [x for x in r if x in allowed]
        return r


@ns.route('/backup-running',
          '/<server>/backup-running',
          endpoint='running_backup')
class RunningBackup(Resource):
    """The :class:`burpui.api.clients.RunningBackup` resource allows you to
    access the status of the server in order to know if there is a running
    backup currently.

    This resource is part of the :mod:`burpui.api.clients` module.
    """
    running_fields = ns.model('Running', {
        'running': fields.Boolean(required=True, description='Is there a backup running right now'),
    })

    @ns.marshal_with(running_fields, code=200, description='Success')
    @ns.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        }
    )
    def get(self, server=None):
        """Tells if a backup is running right now

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
                "running": false
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above.
        """
        j = bui.cli.is_one_backup_running(server)
        # Manage ACL
        if bui.acl and not self.is_admin:
            if isinstance(j, dict):
                new = {}
                for serv in bui.acl.servers(self.username):
                    allowed = bui.acl.clients(self.username, serv)
                    new[serv] = [x for x in j[serv] if x in allowed]
                j = new
            else:
                allowed = bui.acl.clients(self.username, server)
                j = [x for x in j if x in allowed]
        r = False
        if isinstance(j, dict):
            for (k, v) in iteritems(j):
                if r:
                    break
                r = r or (len(v) > 0)
        else:
            r = len(j) > 0
        return {'running': r}


@ns.route('/report',
          '/<server>/report',
          endpoint='clients_report')
class ClientsReport(Resource):
    """The :class:`burpui.api.clients.ClientsReport` resource allows you to
    access general reports about your clients.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``serverName`` is supported when running
    in multi-agent mode.
    """
    parser = ns.parser()
    parser.add_argument('serverName', help='Which server to collect data from when in multi-agent mode')
    stats_fields = ns.model('ClientsStats', {
        'total': fields.Integer(required=True, description='Number of files', default=0),
        'totsize': fields.Integer(required=True, description='Total size occupied by all the backups of this client', default=0),
        'windows': fields.String(required=True, description='Is the client a windows machine', default='unknown'),
    })
    client_fields = ns.model('ClientsReport', {
        'name': fields.String(required=True, description='Client name'),
        'stats': fields.Nested(stats_fields, required=True),
    })
    backup_fields = ns.model('ClientsBackup', {
        'name': fields.String(required=True, description='Client name'),
        'number': fields.Integer(required=True, description='Number of backups on this client', default=0),
    })
    report_fields = ns.model('Report', {
        'backups': fields.Nested(backup_fields, as_list=True, required=True),
        'clients': fields.Nested(client_fields, as_list=True, required=True),
    })

    @api.cache.cached(timeout=1800, key_prefix=cache_key)
    @ns.marshal_with(report_fields, code=200, description='Success')
    @ns.expect(parser)
    @ns.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        },
        responses={
            403: 'Insufficient permissions',
            500: 'Internal failure',
        },
    )
    def get(self, server=None):
        """Returns a global report about all the clients of a given server

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
              "backups": [
                {
                  "name": "client1",
                  "number": 15
                },
                {
                  "name": "client2",
                  "number": 1
                }
              ],
              "clients": [
                {
                  "name": "client1",
                  "stats": {
                    "total": 296377,
                    "totsize": 57055793698,
                    "windows": "unknown"
                  }
                },
                {
                  "name": "client2",
                  "stats": {
                    "total": 3117,
                    "totsize": 5345361,
                    "windows": "true"
                  }
                }
              ]
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above
        """

        server = server or self.parser.parse_args()['serverName']
        j = {}
        # Manage ACL
        if (not bui.standalone and bui.acl and
                (not self.is_admin and
                 server not in
                 bui.acl.servers(self.username))):
            self.abort(403, 'Sorry, you don\'t have any rights on this server')
        clients = []
        if bui.acl and not self.is_admin:
            clients = [{'name': x} for x in bui.acl.clients(self.username, server)]
        else:
            try:
                clients = bui.cli.get_all_clients(agent=server)
            except BUIserverException as e:
                self.abort(500, str(e))
        j = bui.cli.get_clients_report(clients, server)
        return j


@ns.route('/stats',
          '/<server>/stats',
          endpoint='clients_stats')
class ClientsStats(Resource):
    """The :class:`burpui.api.clients.ClientsStats` resource allows you to
    access general statistics about your clients.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``serverName`` is supported when running
    in multi-agent mode.
    """
    parser = ns.parser()
    parser.add_argument('serverName', help='Which server to collect data from when in multi-agent mode')
    client_fields = ns.model('ClientsStatsSingle', {
        'last': fields.DateTime(required=True, dt_format='iso8601', description='Date of last backup'),
        'name': fields.String(required=True, description='Client name'),
        'state': fields.String(required=True, description='Current state of the client (idle, backup, etc.)'),
        'phase': fields.String(description='Phase of the current running backup'),
        'percent': fields.Integer(description='Percentage done', default=0),
    })

    @api.cache.cached(timeout=1800, key_prefix=cache_key)
    @ns.marshal_list_with(client_fields, code=200, description='Success')
    @ns.expect(parser)
    @ns.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        },
        responses={
            403: 'Insufficient permissions',
            500: 'Internal failure',
        },
    )
    def get(self, server=None):
        """Returns a list of clients with their states

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
              [
                {
                  "last": "2015-05-17 11:40:02",
                  "name": "client1",
                  "state": "idle",
                  "phase": "phase1",
                  "percent": 12,
                },
                {
                  "last": "never",
                  "name": "client2",
                  "state": "idle",
                  "phase": "phase2",
                  "percent": 42,
                }
              ]
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above
        """

        server = server or self.parser.parse_args()['serverName']
        try:
            if (not bui.standalone and
                    bui.acl and
                    (not self.is_admin and
                     server not in
                     bui.acl.servers(self.username))):
                self.abort(403, 'Sorry, you don\'t have any rights on this server')
            j = bui.cli.get_all_clients(agent=server)
            if bui.acl and not self.is_admin:
                j = [x for x in j if x['name'] in bui.acl.clients(self.username, server)]
        except BUIserverException as e:
            self.abort(500, str(e))
        return j


@ns.route('/all',
          '/<server>/all',
          endpoint='clients_all')
class AllClients(Resource):
    """The :class:`burpui.api.clients.AllClients` resource allows you to
    retrieve a list of all clients with their associated server (if any).

    An optional ``GET`` parameter called ``serverName`` is supported when
    running in multi-agent mode.
    """
    parser = ns.parser()
    parser.add_argument('serverName', help='Which server to collect data from when in multi-agent mode')
    client_fields = ns.model('AllClients', {
        'name': fields.String(required=True, description='Client name'),
        'agent': fields.String(required=False, default=None, description='Associated Agent name'),
    })

    @api.cache.cached(timeout=1800, key_prefix=cache_key)
    @ns.marshal_list_with(client_fields, code=200, description='Success')
    @ns.expect(parser)
    @ns.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        },
        responses={
            200: 'Success',
            403: 'Insufficient permissions',
        },
    )
    def get(self, server=None):
        """Returns a list of all clients with their associated Agent if any

        **GET** method provided by the webservice.

        The *JSON* returned is:

        ::

            [
              {
                "name": "client1",
                "agent": "agent1"
              },
              {
                "name": "client2",
                "agent": "agent1"
              },
              {
                "name": "client3",
                "agent": "agent2"
              }
            ]


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above
        """
        ret = []
        args = self.parser.parse_args()
        server = server or args['serverName']

        if (server and bui.acl and not self.is_admin and
                server not in bui.acl.servers(self.username)):
            self.abort(403, "You are not allowed to view this server infos")

        if server:
            clients = bui.cli.get_all_clients(agent=server)
            if bui.acl and not self.is_admin:
                ret = [{'name': x, 'agent': server} for x in bui.acl.clients(self.username, server)]
            else:
                ret = [{'name': x['name'], 'agent': server} for x in clients]
            return ret

        if bui.standalone:
            if bui.acl and not self.is_admin:
                ret = [{'name': x} for x in bui.acl.clients(self.username)]
            else:
                ret = [{'name': x['name']} for x in bui.cli.get_all_clients()]
        else:
            grants = {}
            if bui.acl and not self.is_admin:
                for serv in bui.acl.servers(self.username):
                    grants[serv] = bui.acl.clients(self.username, serv)
            else:
                for serv in bui.cli.servers:
                    grants[serv] = 'all'
            for (serv, clients) in iteritems(grants):
                if not isinstance(clients, list):
                    clients = [x['name'] for x in bui.cli.get_all_clients(agent=serv)]
                ret += [{'name': x, 'agent': serv} for x in clients]

        return ret
