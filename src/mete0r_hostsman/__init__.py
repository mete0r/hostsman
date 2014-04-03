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
import re


ADDR_SEP = re.compile('[ \t]+')
NAME_SEP = re.compile('[ \t\r\n]')


def get_hosts(parsed_lines):
    hosts = {}
    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            hostaddr = line['addr']
            for hostname in line['names']:
                hosts[hostname] = hostaddr
    return hosts


def put_hosts(parsed_lines, hosts):

    not_seen = set(hosts.keys())

    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            for hostname, hostaddr in hosts.items():
                if hostname in not_seen:
                    hostname_seen = line_put_host(line, hostname, hostaddr)
                    if hostname_seen:
                        not_seen.remove(hostname)
            if len(line['names']) == 0:
                # skip address without any names
                continue
        yield line

    new_addrs = {}
    for hostname in not_seen:
        hostaddr = hosts[hostname]
        new_addrs.setdefault(hostaddr, []).append(hostname)
    for hostaddr in sorted(new_addrs):
        names = new_addrs[hostaddr]
        yield {
            'type': 'HOSTADDR',
            'addr': hostaddr,
            'names': names,
        }


def line_put_host(line, hostname, hostaddr):
    if hostaddr == line['addr']:
        if hostname not in line['names']:
            line['names'].append(hostname)
        return True
    else:
        if hostname in line['names']:
            line['names'].remove(hostname)
        return False


def delete_hosts(parsed_lines, hosts):
    for line in parsed_lines:
        if line['type'] == 'HOSTADDR':
            for hostname in hosts:
                if hostname in line['names']:
                    line['names'].remove(hostname)
            if len(line['names']) == 0:
                # skip address without any names
                continue
        yield line


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
    names = [name for name in names if name]
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
