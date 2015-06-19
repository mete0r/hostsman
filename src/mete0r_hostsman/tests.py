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
from unittest import TestCase
from unittest import makeSuite
# from pprint import pprint

from mete0r_hostsman import parse
from mete0r_hostsman import render
from mete0r_hostsman import list_hosts
from mete0r_hostsman import get_hosts
from mete0r_hostsman import get_hosts_by_predicate
from mete0r_hostsman import put_hosts
from mete0r_hostsman import delete_hosts
from mete0r_hostsman import HostsManager


class HostsManTest(TestCase):

    maxDiff = None

    def test_parse(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        parsed = list(parsed)
        # pprint(parsed)
        self.assertEquals([{
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', ),
        }, {
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', 'example.tld'),
        }, {
            'line': '127.0.1.2\tb.example.tld\n',
            'line_no': 4,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('b.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }], parsed)

    def test_render(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\texample.tld\n',
        ])
        rendered = render(parsed)
        self.assertEquals(
            '127.0.0.1\tlocalhost\n'
            '# managed by mete0r.hostsman\n'
            '127.0.1.1\texample.tld\n',
            ''.join(rendered))

    def test_list_hosts(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        hosts = dict(list_hosts(parsed))
        self.assertEquals({
            'localhost': '127.0.0.1',
            'example.tld': '127.0.1.1',
            'a.example.tld': '127.0.1.1',
            'b.example.tld': '127.0.1.2',
            'c.example.tld': '127.0.1.2',
        }, hosts)

    def test_get_hosts(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        parsed = list(parsed)
        self.assertEquals({
            'localhost': '127.0.0.1'
        }, dict(get_hosts(parsed, 'localhost')))
        self.assertEquals({
            'localhost': '127.0.0.1'
        }, dict(get_hosts(parsed, ['localhost'])))
        self.assertEquals({
            'localhost': '127.0.0.1',
            'example.tld': '127.0.1.1',
        }, dict(get_hosts(parsed, ['localhost', 'example.tld', 'non-exists'])))

    def test_get_hosts_by_predicate(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        parsed = list(parsed)
        self.assertEquals({
            'a.example.tld': '127.0.1.1',
            'example.tld': '127.0.1.1',
            'b.example.tld': '127.0.1.2',
            'c.example.tld': '127.0.1.2',
        }, dict(get_hosts_by_predicate(parsed, lambda hostname, hostaddr:
                                       hostname != 'localhost')))

    def test_put_hosts(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n'
        ])
        parsed = put_hosts(parsed, {
            'dev.example.tld': '127.0.0.1',
            'example.tld': '127.0.1.1'
        })
        parsed = list(parsed)
        self.assertEquals([{
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', 'dev.example.tld'),
        }, {
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('example.tld', ),
        }], parsed)

    def test_put_hosts_handles_multiple_matching_address_lines(self):
        parsed = parse([
            '127.0.2.1\tfoo.example.tld\n',
            '127.0.2.1\tbar.example.tld\n',
        ])
        parsed = put_hosts(parsed, {
            'baz.example.tld': '127.0.2.1'
        })
        parsed = list(parsed)
        self.assertEquals([{
            'line': '127.0.2.1\tfoo.example.tld\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.2.1',
            'names': ('foo.example.tld', 'baz.example.tld'),
        }, {
            'line': '127.0.2.1\tbar.example.tld\n',
            'line_no': 2,
            'type': 'HOSTADDR',
            'addr': '127.0.2.1',
            'names': ('bar.example.tld',),
        }], parsed)

    def test_delete_hosts(self):
        parsed = parse([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        parsed = delete_hosts(parsed, [
            'example.tld',
            'b.example.tld'
        ])
        parsed = list(parsed)
        self.assertEquals([{
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', ),
        }, {
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }], parsed)
        parsed = delete_hosts(parsed, 'localhost')
        parsed = list(parsed)
        self.assertEquals([{
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }], parsed)

    def test_hostmanager_init(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        self.assertEquals(({
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', ),
        }, {
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', 'example.tld', ),
        }, {
            'line': '127.0.1.2\tb.example.tld\n',
            'line_no': 4,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('b.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }), hostsman.parsed)

    def test_hostmanager_list(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        expected = {
            'localhost': '127.0.0.1',
            'example.tld': '127.0.1.1',
            'a.example.tld': '127.0.1.1',
            'b.example.tld': '127.0.1.2',
            'c.example.tld': '127.0.1.2',
        }
        self.assertEquals(expected, dict(hostsman.list()))
        self.assertEquals(expected, dict(hostsman))

    def test_hostmanager_get(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        self.assertEquals({
            'localhost': '127.0.0.1'
        }, dict(hostsman.get('localhost')))
        self.assertEquals({
            'localhost': '127.0.0.1',
            'example.tld': '127.0.1.1',
        }, dict(hostsman.get(['localhost', 'example.tld', 'non-exists'])))
        self.assertEquals('127.0.0.1', hostsman['localhost'])
        self.assertRaises(KeyError, hostsman.__getitem__, 'non-exists')

    def test_hostmanager_get_by_predicate(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        self.assertEquals({
            'a.example.tld': '127.0.1.1',
            'example.tld': '127.0.1.1',
            'b.example.tld': '127.0.1.2',
            'c.example.tld': '127.0.1.2',
        }, dict(hostsman.get_by_predicate(lambda hostname, hostaddr:
                                          hostname != 'localhost')))

    def test_hostmanager_put(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n'
        ])
        hostsman.put({
            'dev.example.tld': '127.0.0.1',
            'example.tld': '127.0.1.1'
        })
        self.assertEquals(({
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', 'dev.example.tld'),
        }, {
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('example.tld', ),
        }), hostsman.parsed)

    def test_hostmanager_setitem(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n'
        ])
        hostsman['dev.example.tld'] = '127.0.0.1'
        hostsman['example.tld'] = '127.0.1.1'
        self.assertEquals(({
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', 'dev.example.tld'),
        }, {
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('example.tld', ),
        }), hostsman.parsed)

    def test_hostmanager_delete(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        hostsman.delete([
            'example.tld',
            'b.example.tld'
        ])
        self.assertEquals(({
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', ),
        }, {
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }), hostsman.parsed)

    def test_hostmanager_delitem(self):
        hostsman = HostsManager([
            '127.0.0.1\tlocalhost\n',
            '# managed by mete0r.hostsman\n',
            '127.0.1.1\ta.example.tld example.tld\n',
            '127.0.1.2\tb.example.tld\n',
            '127.0.1.2\tc.example.tld\n',
        ])
        del hostsman['example.tld']
        del hostsman['b.example.tld']
        self.assertEquals(({
            'line': '127.0.0.1\tlocalhost\n',
            'line_no': 1,
            'type': 'HOSTADDR',
            'addr': '127.0.0.1',
            'names': ('localhost', ),
        }, {
            'line': '# managed by mete0r.hostsman\n',
            'line_no': 2,
            'type': 'COMMENT',
        }, {
            'line': '127.0.1.1\ta.example.tld example.tld\n',
            'line_no': 3,
            'type': 'HOSTADDR',
            'addr': '127.0.1.1',
            'names': ('a.example.tld', ),
        }, {
            'line': '127.0.1.2\tc.example.tld\n',
            'line_no': 5,
            'type': 'HOSTADDR',
            'addr': '127.0.1.2',
            'names': ('c.example.tld', ),
        }), hostsman.parsed)


def test_suite():
    return makeSuite(HostsManTest)
