# -*- coding: utf-8 -*-
#
#   hostsman : Manage /etc/hosts
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
''' Manage /etc/hosts.

Usage::

    hostsman [-f <file>] list
    hostsman [-f <file>] get <name>...
    hostsman [-f <file>] put <name-address>...
    hostsman [-f <file>] delete <name>...
    hostsman --help

Options::

    -h --help               Show this screen
    -f --file=<file>        hosts file. (default: /etc/hosts)


    <name-address>          <name>=<address> (e.g. example.tld=127.0.0.1)

'''
import logging
import sys

from docopt import docopt

from mete0r_hostsman import load
from mete0r_hostsman import edit


logger = logging.getLogger(__name__)


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc)

    path = args['--file'] or '/etc/hosts'

    if args['list']:
        with open(path) as f:
            hostsman = load(f)
        hosts = hostsman.list()
        print_hosts(hosts)
    elif args['get']:
        with open(path) as f:
            hostsman = load(f)
        hosts = hostsman.get(args['<name>'])
        print_hosts(hosts)
    elif args['put']:
        kvlist = args['<name-address>']
        hosts = parse_name_addr(kvlist)
        with edit(path) as hostsman:
            hostsman.put(hosts)
    elif args['delete']:
        with edit(path) as hostsman:
            hostsman.delete(args['<name>'])
    else:
        logger.error('invalid invocation. try %s --help' % sys.argv[0])
        raise SystemExit(1)


def print_hosts(hosts):
    hosts = dict(hosts)
    for hostname in sorted(hosts):
        hostaddr = hosts[hostname]
        sys.stdout.write('%s\t%s\n' % (hostname, hostaddr))


def rest_to_docopt(doc):
    ''' ReST to docopt conversion
    '''
    return doc.replace('::\n\n', ':\n').replace('``', '')


def parse_name_addr(name_address_list):
    ''' Parse list of <name>=<address> lists into a dict.
    '''
    return dict(kv.split('=', 1) for kv in name_address_list)
