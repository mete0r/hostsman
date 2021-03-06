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
from __future__ import with_statement
from contextlib import contextmanager
import re


__version__ = '0.0.0'


ADDR_SEP = re.compile('[ \t]+')
NAME_SEP = re.compile('[ \t\r\n]')


def list_hosts(parsed_lines):
    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            hostaddr = line['addr']
            for hostname in line['names']:
                yield hostname, hostaddr


def get_hosts(parsed_lines, hosts):
    if isinstance(hosts, basestring):
        hosts = (hosts, )
    return get_hosts_by_predicate(parsed_lines, predicate_hostname(hosts))


def get_hosts_by_predicate(parsed_lines, predicate):
    for hostname, hostaddr in list_hosts(parsed_lines):
        if predicate(hostname, hostaddr):
            yield hostname, hostaddr


def predicate_hostname(hosts):
    hosts = set(hostname.upper() for hostname in hosts)
    return lambda hostname, hostaddr: hostname.upper() in hosts


def predicate_hostaddr(addrs):
    addrs = set(addr.strip() for addr in addrs)
    return lambda hostname, hostaddr: hostaddr.strip() in addrs


def put_hosts(parsed_lines, hosts):

    new_hostnames = set(hosts)

    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            for hostname, hostaddr in hosts.items():
                if hostaddr == line['addr'] and hostname in new_hostnames:
                    line = line_append_hostname_if_missing(line, hostname)
                    new_hostnames.remove(hostname)
                else:
                    line = line_delete_hostname(line, hostname)
            if len(line['names']) == 0:
                # skip address without any names
                continue
        yield line

    # add new hosts: grouped by address

    new_addrs = {}
    for hostname in new_hostnames:
        hostaddr = hosts[hostname]
        new_addrs.setdefault(hostaddr, []).append(hostname)
    for hostaddr in sorted(new_addrs):
        names = new_addrs[hostaddr]
        yield {
            'type': 'HOSTADDR',
            'addr': hostaddr,
            'names': tuple(names),
        }


def delete_hosts(parsed_lines, hosts):
    if isinstance(hosts, basestring):
        hosts = (hosts, )
    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            for hostname in hosts:
                line = line_delete_hostname(line, hostname)
            if len(line['names']) == 0:
                # skip address without any names
                continue
        yield line


def line_contains_hostname(line, hostname):
    names = set(name.upper() for name in line['names'])
    return hostname.upper() in names


def line_append_hostname_if_missing(line, hostname):
    if not line_contains_hostname(line, hostname):
        return line_append_hostname(line, hostname)
    return line


def line_append_hostname(line, hostname):
    return dict(line, names=line['names'] + (hostname, ))


def line_delete_hostname(line, hostname):
    hostnames = line['names']
    hostnames = tuple(name for name in hostnames
                      if name.upper() != hostname.upper())
    return dict(line, names=hostnames)


def parse(lines):
    for line_no, line in enumerate(lines):
        ev = {
            'line': line,
            'line_no': line_no + 1,
        }
        if line.startswith('#'):
            ev['type'] = 'COMMENT'
        else:
            try:
                ev['type'] = 'HOSTADDR'
                ev.update(parse_hostaddr_line(line))
                ev['type'] = 'HOSTADDR'
            except Exception as e:
                ev['type'] = 'UNRECOGNIZED'
                ev['exception'] = e
        yield ev


def parse_hostaddr_line(line):
    addr, name_trail = ADDR_SEP.split(line, 1)
    names = NAME_SEP.split(name_trail)
    names = (name.strip() for name in names)
    names = (name for name in names if name)
    names = tuple(names)
    return {
        'addr': addr,
        'names': names
    }


def render(parsed_lines):
    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            yield render_hostaddr_line(line)
        else:
            yield line['line']


def render_hostaddr_line(line):
    return '%s\t%s\n' % (line['addr'], ' '.join(line['names']))


class HostsManager:

    def __init__(self, lines=()):
        self.parsed = tuple(parse(lines))

    def list(self):
        return list_hosts(self.parsed)

    __iter__ = list

    def get(self, hostnames=()):
        return get_hosts(self.parsed, hostnames)

    def get_by_predicate(self, predicate):
        return get_hosts_by_predicate(self.parsed, predicate)

    def __getitem__(self, key):
        for hostname, hostaddr in self.get(key):
            if hostname == key:
                return hostaddr
        raise KeyError(key)

    def put(self, hosts):
        self.parsed = tuple(put_hosts(self.parsed, hosts))

    def __setitem__(self, hostname, hostaddr):
        self.put({hostname: hostaddr})

    def delete(self, hostnames):
        self.parsed = tuple(delete_hosts(self.parsed, hostnames))

    __delitem__ = delete

    def render(self):
        return render(self.parsed)


def load(f):
    return HostsManager(f)


def dump(hostsman, f):
    for line in hostsman.render():
        f.write(line)


@contextmanager
def edit(path='/etc/hosts'):
    with open(path, 'r+') as f:
        hostsman = load(f)

        yield hostsman

        f.seek(0)
        dump(hostsman, f)
        f.truncate()
