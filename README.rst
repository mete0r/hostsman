mete0r.hostsman
===============

Manage /etc/hosts file.


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
