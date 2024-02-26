# pylint: disable=import-outside-toplevel,global-statement,C0209
from __future__ import print_function
import os
import re
import sys
import platform

MAMBA_ROOT_PREFIX = None
MAMBA_EXE = None
MAMBA_PATH = None


def check_platform():
    if platform.system() != 'Windows':
        print('This script is for Windows only.')
        sys.exit(1)


def resolve_micromamba_env_entry():
    username = os.getenv('USERNAME')
    ps_path = os.path.join('C:\\Users', username, 'Documents', 'WindowsPowerShell', 'profile.ps1')
    if os.path.exists(ps_path):
        get_env_from_ps(ps_path)
    else:
        get_env_from_registry_and_bat()


def get_env_from_ps(ps_path):
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    with open(ps_path, 'r', encoding="utf-8") as f:
        for line in f:
            match_prefix = re.search(r'\$Env:MAMBA_ROOT_PREFIX\s*=\s*"([^"]+)"', line)
            match_exe = re.search(r'\$Env:MAMBA_EXE\s*=\s*"([^"]+)"', line)
            MAMBA_ROOT_PREFIX = match_prefix.group(1) if match_prefix else MAMBA_ROOT_PREFIX
            MAMBA_EXE = match_exe.group(1) if match_exe else MAMBA_EXE


def get_env_from_registry_and_bat():
    # As mamba_hook.bat located on $MAMBA_ROOT_PREFIX/condabin, and we don't know $MAMBA_ROOT_PREFIX
    # So we need to access registry to get $MAMBA_ROOT_PREFIX and mamba_hook.bat path
    # see https://github.com/mamba-org/mamba/issues/2482#issuecomment-1519054884
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    try:
        import winreg as reg
    except ImportError:
        import _winreg as reg
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Command Processor',
                          0, reg.KEY_READ)
        mamba_hook_path, _ = reg.QueryValueEx(key, 'AutoRun')
        reg.CloseKey(key)
        if mamba_hook_path:
            mamba_hook_path = mamba_hook_path.strip('"')
            MAMBA_ROOT_PREFIX = os.path.dirname(os.path.dirname(mamba_hook_path))
            with open(mamba_hook_path, 'r', encoding="utf-8") as f:
                for line in f:
                    match = re.search(r'@SET "MAMBA_EXE=([^"]+)"', line)
                    MAMBA_EXE = match.group(1) if match else MAMBA_EXE
    except WindowsError:
        pass


def manually_input_path_wizard():
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    print('Cannot find MAMBA_ROOT_PREFIX and MAMBA_EXE from PowerShell profile or registry!')
    print('Please input MAMBA_ROOT_PREFIX and MAMBA_EXE manually.')
    MAMBA_ROOT_PREFIX, MAMBA_EXE = input('MAMBA_ROOT_PREFIX: '), input('MAMBA_EXE: ')
    if not (os.path.exists(MAMBA_ROOT_PREFIX) and os.path.exists(MAMBA_EXE)):
        print('Invalid path! Please input valid path.')
        sys.exit(1)


def generate_bat_file():
    global MAMBA_PATH
    python_list = ["python", "python3", "python2"]
    python_path = next((os.getenv(env) for env in python_list if os.getenv(env)), sys.executable)
    bat_file = 'conda.bat'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not (MAMBA_ROOT_PREFIX and MAMBA_EXE):
        manually_input_path_wizard()
    MAMBA_PATH = os.path.dirname(MAMBA_EXE)
    with open(bat_file, 'w', encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('set MAMBA_ROOT_PREFIX={}\n'.format(MAMBA_ROOT_PREFIX))
        f.write('set MAMBA_EXE={}\n'.format(MAMBA_EXE))
        f.write('set PATH=%PATH%;{}\n'.format(MAMBA_PATH))
        f.write('"{}" "{}" %*'.format(python_path, os.path.join(current_dir, 'conda')))
    print('Successfully Generated micromamba.bat at {}'.format(os.path.abspath(bat_file)))


if __name__ == '__main__':
    check_platform()
    resolve_micromamba_env_entry()
    generate_bat_file()
