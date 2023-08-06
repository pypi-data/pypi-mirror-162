#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#
"""Install root and client certificates on different OSes."""

import subprocess
from pathlib import Path

from aos_keys.common import ca_certificate, AosKeysError


def _execute_command(command):
    completed_process = subprocess.run(command, capture_output=True)
    if completed_process.returncode == 0:
        return

    error = completed_process.stderr
    if not error and completed_process.stdout:
        error = completed_process.stdout
    raise AosKeysError(f'Failed to install certificate:\n {error.decode("utf8")}')


def install_root_certificate_macos():
    """Install root certificate on current user's Trusted Root CA."""
    with ca_certificate() as server_certificate_path:
        command = [
            'sudo',
            'security',
            'add-trusted-cert',
            '-d',
            '-r',
            'trustRoot',
            '-k',
            '/Library/Keychains/System.keychain',
            server_certificate_path,
        ]
        _execute_command(command)


def install_root_certificate_windows():
    """Install root certificate on current user's Trusted Root CA."""
    with ca_certificate() as server_certificate_path:
        command = ['certutil', '-addstore', '-f', '-user', 'Root', server_certificate_path]
        _execute_command(command)


def install_root_certificate_linux():
    """Install root certificate on linux host."""
    command = ['dpkg', '-s', 'update-ca-certificates']
    completed_process = subprocess.run(command, check=True)
    if completed_process.returncode > 0:
        raise AosKeysError(
            'Failed to install certificate. Required package missing',
            'Install update-ca-certificates first with command: sudo apt install ca-certificates',
        )

    with ca_certificate() as server_certificate_path:
        if not Path('/usr/local/share/ca-certificates/').exists():
            command = ['sudo', 'mkdir', '/usr/local/share/ca-certificates/']
            completed_process = subprocess.run(command, check=True)
        if not Path('/usr/local/share/ca-certificates/1rootCA.crt').exists():
            command = ['sudo', 'cp', server_certificate_path, '/usr/local/share/ca-certificates/1rootCA.crt']
            completed_process = subprocess.run(command, check=True)
        command = ['sudo', 'update-ca-certificates']
        completed_process = subprocess.run(command, check=True)


def install_user_certificate_windows(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.
    """
    command = ['certutil', '-addstore', '-f', '-user', 'My', certificate_path]
    print(command)
    _execute_command(command)


def install_user_certificate_linux(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.
    """
    command = ['certutil', '-addstore', '-f', '-user', 'My', certificate_path]
    _execute_command(command)


def install_user_certificate_macos(certificate_path: Path):
    """Install client certificate to the Windows Personal store.

    Args:
        certificate_path: path to certificate which will be installed.
    """
    command = ['certutil', '-addstore', '-f', '-user', 'My', certificate_path]
    _execute_command(command)
