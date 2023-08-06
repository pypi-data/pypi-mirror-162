# -*- coding: utf-8 -*-

"""
Napalm driver for ArubaOS 505 Wi-Fi Device using SSH.
Read https://napalm.readthedocs.io for more information.
"""

#from __future__ import unicode_literals
from datetime import datetime
import socket

# import third party lib
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException

# import NAPALM Base
import napalm.base.helpers
from napalm.base.base import NetworkDriver
from napalm.base.exceptions import (
    ConnectionException,
    CommandErrorException,
    CommitError,
)


import copy
import functools
import os
import re
import socket
import telnetlib
import tempfile
import uuid
from collections import defaultdict

from netaddr import IPNetwork
from netaddr.core import AddrFormatError
from netmiko import FileTransfer, InLineTransfer

import napalm.base.constants as C
import napalm.base.helpers
from napalm.base.base import NetworkDriver
from napalm.base.exceptions import (
    ReplaceConfigException,
    MergeConfigException,
    ConnectionClosedException,
    CommandErrorException,
)
from napalm.base.helpers import (
    canonical_interface_name,
    transform_lldp_capab,
    textfsm_extractor,
    split_interface,
    abbreviated_interface_name,
    generate_regex_or,
    sanitize_configs,
)
from napalm.base.netmiko_helpers import netmiko_args
###
from netmiko import ConnectHandler
import netmiko
from netmiko import ssh_exception
from netmiko.ssh_exception import *
from netmiko.ssh_exception import NetmikoAuthenticationException
from netmiko.ssh_exception import NetmikoTimeoutException
from netmiko.ssh_exception import SSHException
###

SECONDS = 1
MINUTE_SECONDS = 60
HOUR_SECONDS = 3600
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS


class ArubaOS505(NetworkDriver):
    """Napalm driver for ArubaOS 505 Wi-Fi Device."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """NAPALM ArubaOS 505 Wi-Fi Handler."""
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        # Get optional arguments
        if optional_args is None:
            optional_args = {}

        # Netmiko possible arguments
        netmiko_argument_map = {
            'port': None,
            'verbose': False,
            'conn_timeout': self.timeout,
            'global_delay_factor': 1,
            'use_keys': False,
            'key_file': None,
            'ssh_strict': False,
            'system_host_keys': False,
            'alt_host_keys': False,
            'alt_key_file': '',
            'ssh_config_file': None,
            'allow_agent': False,
            'keepalive': 30
        }

        # Build dict of any optional Netmiko args
        self.netmiko_optional_args = {
            k: optional_args.get(k, v)
            for k, v in netmiko_argument_map.items()
        }

        self.transport = optional_args.get('transport', 'ssh')
        self.port = optional_args.get('port', 22)
        self.profile = ["ArubaOS"]

    def open(self):
        """Open a connection to the device."""
        try:
            if self.transport == 'ssh':
                device_type = 'aruba_os'
            else:
                raise ConnectionException("Unknown transport: {}".format(self.transport))

            self.device = ConnectHandler(device_type=device_type,
                                         host=self.hostname,
                                         username=self.username,
                                         password=self.password,
                                         **self.netmiko_optional_args)

        except NetMikoTimeoutException:
            raise ConnectionException('Cannot connect to {}'.format(self.hostname))

    def close(self):
        """Close the connection to the device."""
        self.device.disconnect()
        self.device = None

    def is_alive(self):
        """Return a flag with the state of the SSH connection."""
        null = chr(0)
        try:
            if self.device is None:
                return {'is_alive': False}
            else:
                # Try sending ASCII null byte to maintain the connection alive
                self.device.send_command(null)
        except (socket.error, EOFError):
            # If unable to send, we can tell for sure that the connection is unusable,
            # hence return False.
            return {'is_alive': False}
        return {
            'is_alive': self.device.remote_conn.transport.is_active()
        }

    def get_config(self, retrieve="all", full=False, sanitized=False):
        """
        Get config from device.
        Returns the running configuration as dictionary.
        The candidate and startup are always empty string for now,
        """

        configs = {
            "running": "",
            "startup": "No Startup",
            "candidate": "No Candidate"
        }

        if retrieve.lower() in ('running', 'all'):
            command = "show running-config"
            output = self.device.send_command(command)
            if output:
                configs['running'] = output
                data = str(configs['running']).split("\n")
                non_empty_lines = [line for line in data if line.strip() != ""]

                string_without_empty_lines = ""
                for line in non_empty_lines:
                    string_without_empty_lines += line + "\n"
                configs['running'] = string_without_empty_lines

        if retrieve.lower() in ('startup', 'all'):
            pass
        return configs

    def get_facts(self):
        """Return a set of facts from the devices."""

        # Initialize the vars to zero
        (years, weeks, days, hours, minutes, seconds) = (0, 0, 0, 0, 0, 0)
        vendor = "Hewlett Packard"
        model = ""
        os_version = ""
        uptime = ""

        fqdn = ""
        serial_number = ""
        hostname_ = ""

        configs = {}
        show_version_output = self.device.send_command("show version")
        show_summary_output = self.device.send_command("show summary")

        # processing 'show version' output
        configs['show_version'] = show_version_output
        show_version_data = str(configs['show_version']).split("\n")
        show_version_non_empty_lines = [line for line in show_version_data if line.strip() != ""]

        show_version_string_ = ""
        for line in show_version_non_empty_lines:
            show_version_string_ += line + "\n"

        if show_version_string_:
            for line in show_version_string_.splitlines():
                if "MODEL:" in line:
                    model, os_version = line.split(',')
                if "AP uptime is" in line:
                    uptimes_records = [int(i) for i in line.split() if i.isnumeric()]
                    if uptimes_records and len(uptimes_records) >= 5:
                        weeks, days, hours, minutes, seconds = uptimes_records
                        uptime = sum([(years * YEAR_SECONDS), (weeks * WEEK_SECONDS), (days * DAY_SECONDS),
                                      (hours * HOUR_SECONDS), (minutes * MINUTE_SECONDS), (seconds * SECONDS), ])

        # processing 'show summary' output
        configs['running_'] = show_summary_output
        data = str(configs['running_']).split("\n")
        non_empty_lines = [line for line in data if line.strip() != ""]

        show_summary_string_ = ""
        for line in non_empty_lines:
            show_summary_string_ += line + "\n"

        if show_summary_string_:
            data_l = show_summary_string_.splitlines()
            for l in data_l:
                if "Name" in l and not hostname_:
                    hostname_ = f"{l.split(':')[1].lower()}"
                if "DNSDomain" in l and hostname_:
                    fqdn = f"{hostname_}.{l.split(':')[1]}"
                if "Serial Number" in l:
                    serial_number = l.split(':')[1]

        return {
            "hostname": str(hostname_),
            "fqdn": fqdn,
            "vendor": str(vendor),
            "model": str(model),
            "serial_number": str(serial_number),
            "os_version": str(os_version).strip(),
            "uptime": uptime,
            }

