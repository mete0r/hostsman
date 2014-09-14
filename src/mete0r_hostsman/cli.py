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

    hostsman [--file=<file>] get [<name>...]
    hostsman [--file=<file>] put [<name-address>...]
    hostsman [--file=<file>] delete [<name>...]
    hostsman --help

Options::

    -h --help               Show this screen
       --file=<file>        hosts file. (default: /etc/hosts)


    <name-address>          <name>=<address> (e.g. example.tld=127.0.0.1)

'''
import logging
import sys

from docopt import docopt

from mete0r_hostsman import parse
from mete0r_hostsman import render
from mete0r_hostsman import get_hosts
from mete0r_hostsman import put_hosts
from mete0r_hostsman import delete_hosts


logger = logging.getLogger(__name__)


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc)

    path = args['--file'] or '/etc/hosts'

    if args['get']:
        print_hosts(path, args['<name>'])
    elif args['put']:
        kvlist = args['<name-address>']
        update = lambda parsed: put_hosts(parsed, parse_name_addr(kvlist))
        update_file(path, update)
    elif args['delete']:
        update = lambda parsed: delete_hosts(parsed, args['<name>'])
        update_file(path, update)
    else:
        logger.error('invalid invocation. try %s --help' % sys.argv[0])
        raise SystemExit(1)


def print_hosts(path, hostnames):
    with file(path, 'rb') as f:
        parsed = parse(f)
        hosts = dict(get_hosts(parsed))
        for hostname in sorted(hostnames or hosts):
            hostaddr = hosts.get(hostname)
            sys.stdout.write('%s\t%s\n' % (hostname, hostaddr))


def update_file(path, update):
    with file(path, 'rb') as f:
        parsed = parse(f)
        updated = update(parsed)
        rendered = render(updated)
        with file(path, 'rb+') as g:
            for line in rendered:
                g.write(line)
            g.truncate()


def rest_to_docopt(doc):
    ''' ReST to docopt conversion
    '''
    return doc.replace('::\n\n', ':\n').replace('``', '')


def parse_name_addr(name_address_list):
    ''' Parse list of <name>=<address> lists into a dict.
    '''
    return dict(kv.split('=', 1) for kv in name_address_list)
