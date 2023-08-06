# -*- coding: utf-8 -*-
"""NAPALM ArubaOS Five zero five Handler."""

from __future__ import print_function
from __future__ import unicode_literals
import socket
import json
from napalm.base import constants as c
from netmiko import ConnectHandler
from napalm.base.base import NetworkDriver


# Easier to store these as constants
SECONDS = 1
MINUTE_SECONDS = 60
HOUR_SECONDS = 3600
DAY_SECONDS = 24 * HOUR_SECONDS
WEEK_SECONDS = 7 * DAY_SECONDS
YEAR_SECONDS = 365 * DAY_SECONDS



class ArubaFDriver(NetworkDriver):
    """NAPALM ArubaOS Five zero five Handler."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """NAPALM Cisco IOS Handler."""
        if optional_args is None:
            optional_args = {}
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

        self.transport = optional_args.get('transport', 'ssh')

        # Netmiko possible arguments
        netmiko_argument_map = {
            'port': None,
            'secret': '',
            'verbose': False,
            'keepalive': 30,
            'global_delay_factor': 1,
            'use_keys': False,
            'key_file': None,
            'ssh_strict': False,
            'system_host_keys': False,
            'alt_host_keys': False,
            'alt_key_file': '',
            'ssh_config_file': None,
            'allow_agent': False,
        }

        # Build dict of any optional Netmiko args
        self.netmiko_optional_args = {}
        for k, v in netmiko_argument_map.items():
            try:
                self.netmiko_optional_args[k] = optional_args[k]
            except KeyError:
                pass

        default_port = {
            'ssh': 22,
            'telnet': 23
        }
        self.port = optional_args.get('port', default_port[self.transport])

        self.device = None
        self.config_replace = False
        self.interface_map = {}
        self.profile = ["ArubaOS"]

    def open(self):
        """Open a connection to the device."""
        device_type = 'aruba_os'
        if self.transport == 'ssh':
            device_type = 'aruba_os'
        self.device = ConnectHandler(device_type=device_type,
                                     host=self.hostname,
                                     username=self.username,
                                     password=self.password,
                                     **self.netmiko_optional_args)
        # ensure in enable mode
        ## self.device.enable()

    def close(self):
        """Close the connection to the device."""
        self.device.disconnect()

    def is_alive(self):
        """Returns a flag with the state of the connection."""
        null = chr(0)
        if self.device is None:
            return {'is_alive': False}
        else:
            # SSH
            try:
                # Try sending ASCII null byte to maintain the connection alive
                self.device.write_channel(null)
                return {'is_alive': self.device.remote_conn.transport.is_active()}
            except (socket.error, EOFError):
                # If unable to send, we can tell for sure that the connection is unusable
                return {'is_alive': False}
        ## return {'is_alive': False}

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


    def show_summary_sanitizer(self, data):
        """ Collects the fqdn and the serial number from the 'show summary'
        :returns a tuple with two values (hostname, fqdn, serial_number)
        """

        fqdn = ""
        serial_number = ""
        hostname_ = ""

        if data:
            data_l = data.strip().splitlines()

            for l in data_l:
                if "Name" in l and not hostname_:
                    hostname_ = f"{l.split(':')[1].lower()}"
                if "DNSDomain" in l and hostname_:
                    fqdn = f"{hostname_}.{l.split(':')[1]}"
                if "Serial Number" in l :
                    serial_number = l.split(':')[1]
        return hostname_, fqdn, serial_number


    def show_version_sanitizer(self, data):
        """ Collects the vendor, model, os version and uptime from the 'show version'
        :returns a tuple with two values (vendor, model, os version, uptime)
        """

        # Initialize to zero
        (years, weeks, days, hours, minutes, seconds) = (0, 0, 0, 0, 0, 0)

        vendor = "Hewlett Packard"
        model = ""
        os_version = ""
        uptime = ""

        if data:
            data_l = data.strip().splitlines()
            for l in data_l:
                if "MODEL" in l:
                    model, os_version = l.split(',')
                if "AP uptime is" in l:
                    tmp_uptime = l.replace("AP uptime is", "").split()
                    uptimes_records = [int(i) for i in tmp_uptime if i.isnumeric()]

                    if uptimes_records and len(uptimes_records) >= 5:
                        weeks, days, hours, minutes, seconds = uptimes_records
                        uptime = float(sum([(years * YEAR_SECONDS), (weeks * WEEK_SECONDS), (days * DAY_SECONDS),
                                            (hours * HOUR_SECONDS), (minutes * MINUTE_SECONDS), (seconds * SECONDS), ]))
                    if uptimes_records and len(uptimes_records) == 4:
                        weeks, days, hours, minutes = uptimes_records
                        uptime = float(sum([(years * YEAR_SECONDS), (weeks * WEEK_SECONDS), (days * DAY_SECONDS),
                                            (hours * HOUR_SECONDS), (minutes * MINUTE_SECONDS), (seconds * SECONDS), ]))

        return vendor, model, os_version, uptime



    def get_facts(self):
        """Return a set of facts from the devices"""

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
        vendor, model, os_version, uptime = self.show_version_sanitizer(show_version_string_)

        # processing 'show summary' output
        configs['running_'] = show_summary_output
        data = str(configs['running_']).split("\n")
        non_empty_lines = [line for line in data if line.strip() != ""]

        show_summary_string_ = ""
        for line in non_empty_lines:
            show_summary_string_ += line + "\n"
        hostname_, fqdn_, serial_number_ = self.show_summary_sanitizer(show_summary_string_)

        return {
            "hostname": str(hostname_),
            "fqdn": fqdn_,
            "vendor": str(vendor),
            "model": str(model),
            "serial_number": str(serial_number_),
            "os_version": str(os_version).strip(),
            "uptime": uptime,
        }


    def get_ping(self):
        """ping"""
        bad_responses = [
            "not known", "Name or service not known", "Error", "error",
             "fail", "Fail", "Destination Host Unreachable", "Destination",
             "Unreachable", "estination", "reachable", "connect"
        ]

        self.destination = self.hostname
        command = "ping {}".format(self.destination)
        output = self.device.send_command(command)
        output = str(output)

        ping_dict = {}
        if output:
            for i in bad_responses:
                if i in output:
                    ping_dict["error"] = "disconnected"
                    break
        elif output and len(output) > 10:
            ping_dict["success"] = "connected"
        #return ping_dict
        return output


    def get_lldp_neighbors(self):
        ## TODO: testing for HP SW only for now"
        vendor = ""
        system_name = ""            # System name: ZAF-RH-2-SW-1
        interface_description = ""  # Interface description: A21, ID: 21, MTU: 0

        lldp = {}
        command = ["show ap debug lldp neighbor interface eth0"] #  for HP SW only
        result = self.device.send_command(command)
        data = [line.strip() for line in result.splitlines()]


        for line in data:
            if line:
                if "System name:" in line:
                    system_name = line.split()[2]
                    #print(f"{line.split()[2]}\n")
                if "Interface description:" in line:
                    interface_description = line.split()[2].replace(",", "")
                    #print(f"{line.split()[2]}\n")
                if line.startswith("HP"):
                    if "Switch" in line and "revision" in line and "ROM" in line:
                        vendor = "HP"
                        #print(line)


        lldp["Eth0"] = [{"hostname": system_name, "port": interface_description}]

        return lldp







