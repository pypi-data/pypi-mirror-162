# -*- coding: utf-8 -*-
import ctypes
import os.path
import platform
import subprocess
import warnings
# noinspection PyCompatibility
import winreg
from contextlib import contextmanager
from enum import Enum
from typing import Any, Generator, Mapping, Optional

__all__ = [
    'RebootCause',
    'reboot_check',
    'wake_lock'
]


LINUX_REBOOT_REQUIRED_PATH = '/var/run/reboot-required'

WIN_ES_CONTINUOUS = 0x80000000
WIN_ES_SYSTEM_REQUIRED = 0x00000001
WIN_ES_DISPLAY_REQUIRED = 0x00000002

# Determine platform
_OS = platform.system()


class RebootCause(Enum):
    NONE = 'none'

    LINUX_REBOOT_REQUIRED = 'Linux system update'

    WIN_FORCE_WU = 'Windows Update'
    WIN_FORCE_SCCM = 'Windows SCCM reboot requested'
    WIN_FORCE_SCCM_HARD = 'Windows SCCM hard reboot requested'

    WIN_CBS = 'Windows add/remove roles and/or features'
    WIN_DOMAIN_JOIN = 'Windows pending domain join'
    WIN_SYSTEM_RENAME = 'Windows pending system rename'
    WIN_FILE_RENAME = 'Windows pending system file rename operations'

    @property
    def force(self) -> bool:
        """ True if this reboot cause can force the system to restart at a scheduled time.

        :return: True if reboot cause may result in force scheduled reboot, False otherwise
        """
        # Windows update forces a reboot on most installations
        return self in (RebootCause.WIN_FORCE_WU, RebootCause.WIN_FORCE_SCCM, RebootCause.WIN_FORCE_SCCM_HARD)

    def __bool__(self) -> bool:
        return self != RebootCause.NONE


def _win_reg_dict(hkey: int, sub_key: str) -> Mapping[str, Any]:
    reg_dict = {}

    with winreg.OpenKey(hkey, sub_key) as key:
        key_info = winreg.QueryInfoKey(key)

        for n in range(key_info[1]):
            value_name, value_data, value_type = winreg.EnumValue(key, n)

            if value_type == winreg.REG_NONE:
                value_data = None

            reg_dict[value_name] = value_data

    return reg_dict


def _win_powershell_wmi_check(name: str, flag: str) -> Optional[bool]:
    ps_process = subprocess.Popen(
        f"powershell.exe (icim -namespace root\\ccm\\clientsdk -ClassName CCM_ClientUtilities -Name "
        f"{name}).{flag}",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_process_out, ps_process_err = ps_process.communicate()

    if len(ps_process_err) == 0:
        ps_response = ps_process_out.decode().strip()

        if ps_response == 'True':
            return True
        elif ps_response == 'False':
            return False
        else:
            raise ValueError(f"Unexpected response from PowerShell call: {ps_process_out!r}")

    return None


def reboot_check() -> Optional[RebootCause]:
    # Determine platform
    if _OS == 'Windows':
        # Windows update
        reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE,
                                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\')

        if 'RebootPending' in reg_key:
            return RebootCause.WIN_FORCE_WU

        # SCCM client via WMI
        if _win_powershell_wmi_check('DetermineIfRebootPending', 'IsHardRebootPending'):
            return RebootCause.WIN_FORCE_SCCM_HARD

        if _win_powershell_wmi_check('DetermineIfRebootPending', 'RebootPending'):
            return RebootCause.WIN_FORCE_SCCM

        # Component Based Servicing
        reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE,
                                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\')

        if 'RebootPending' in reg_key:
            return RebootCause.WIN_CBS

        # Domain join
        reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE,
                                'SYSTEM\\CurrentControlSet\\Services\\Netlogon')

        if 'JoinDomain' in reg_key or 'AvoidSpnSet' in reg_key:
            return RebootCause.WIN_DOMAIN_JOIN

        # Computer renamed
        active_reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE,
                                       'SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ActiveComputerName\\')
        conf_reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE,
                                     'SYSTEM\\CurrentControlSet\\Control\\ComputerName\\ComputerName\\')

        if active_reg_key['ComputerName'] != conf_reg_key['ComputerName']:
            return RebootCause.WIN_SYSTEM_RENAME

        # System file rename operations
        reg_key = _win_reg_dict(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\')

        if 'PendingFileRenameOperations' in reg_key and len(reg_key['PendingFileRenameOperations']) > 0:
            return RebootCause.WIN_FILE_RENAME

        return RebootCause.NONE
    elif _OS == 'linux':
        if os.path.exists(LINUX_REBOOT_REQUIRED_PATH):
            return RebootCause.LINUX_REBOOT_REQUIRED

        return RebootCause.NONE
    else:
        warnings.warn(f"Reboot check not supported on platform {_OS!r}")

    return None


@contextmanager
def wake_lock(display_lock: bool = False) -> Generator[None, None, None]:
    """ Create contact manager providing a wake lock on supported platforms.

    :return: None
    """
    # Determine platform
    if _OS == 'Windows':
        # Set wake lock
        state = WIN_ES_CONTINUOUS | WIN_ES_SYSTEM_REQUIRED

        if display_lock:
            state |= WIN_ES_DISPLAY_REQUIRED

        ctypes.windll.kernel32.SetThreadExecutionState(state)

        yield

        # Clear wake lock
        ctypes.windll.kernel32.SetThreadExecutionState(WIN_ES_CONTINUOUS)
    else:
        warnings.warn(f"Wake lock not supported on platform {_OS!r}")
        yield
