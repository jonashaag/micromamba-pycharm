from __future__ import print_function
import os
import re
import sys
import locale
import platform
import subprocess

MAMBA_ROOT_PREFIX = None
MAMBA_EXE = None


def check_platform():
    if platform.system() != 'Windows':
        print('This script is for Windows only.')
        sys.exit(2)


def get_prefix_exe_from_ps(ps_path):
    with open(ps_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    # $MAMBA_ROOT_PREFIX must set with $MAMBA_EXE
    match_prefix_list = [re.search(r'\$Env:MAMBA_ROOT_PREFIX\s*=\s*"([^"]+)"', line) for line in lines]
    match_exe_list = [re.search(r'\$Env:MAMBA_EXE\s*=\s*"([^"]+)"', line) for line in lines]
    match_prefix = next((match for match in match_prefix_list if match is not None), None)
    match_exe = next((match for match in match_exe_list if match is not None), None)
    return (match_prefix.group(1), match_exe.group(1)) if match_prefix and match_exe else (None, None)


def fetch_prefix_from_ps_init():
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    powershell_list = ["powershell", "pwsh", "pwsh-preview"]
    profile_prefix = "$PROFILE.CurrentUserAllHosts"
    for ps in powershell_list:
        try:
            out = subprocess.check_output([ps, "-NoProfile", "-Command", profile_prefix],
                                          encoding=locale.getpreferredencoding()).strip()
            MAMBA_ROOT_PREFIX, MAMBA_EXE = get_prefix_exe_from_ps(out)
            if MAMBA_ROOT_PREFIX and MAMBA_EXE:
                print('Found MAMBA_ROOT_PREFIX from PowerShell profile: {}'.format(MAMBA_ROOT_PREFIX))
                print('Found MAMBA_EXE from PowerShell profile: {}'.format(MAMBA_EXE))
                return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return False


def get_exe_from_bat(bat_path):
    with open(bat_path, 'r', encoding="utf-8") as f:
        match = [re.search(r'@SET "MAMBA_EXE=([^"]+)"', line) for line in f]
    match_exe = next((match for match in match if match is not None), None)
    return match_exe.group(1) if match_exe else None


# noinspection PyUnresolvedReferences
def fetch_prefix_from_bat_init():
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    try:
        import winreg as reg
    except ImportError:
        import _winreg as reg
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Command Processor',
                          0, reg.KEY_READ)
        mamba_hook_path, _ = reg.QueryValueEx(key, 'AutoRun')
        mamba_hook_path = mamba_hook_path.replace('"', '')
        reg.CloseKey(key)
        MAMBA_ROOT_PREFIX = os.path.dirname(os.path.dirname(mamba_hook_path)) if mamba_hook_path else None
        MAMBA_EXE = get_exe_from_bat(mamba_hook_path) if mamba_hook_path else None
    except WindowsError:
        pass
    if MAMBA_ROOT_PREFIX and MAMBA_EXE:
        print('Found MAMBA_ROOT_PREFIX from registry: {}'.format(MAMBA_ROOT_PREFIX))
        print('Found MAMBA_EXE from registry: {}'.format(MAMBA_EXE))
        return True
    return False


def manually_input_path_wizard():
    global MAMBA_ROOT_PREFIX, MAMBA_EXE
    print('Cannot find MAMBA_ROOT_PREFIX and MAMBA_EXE from PowerShell profile or registry!')
    print('Please input MAMBA_ROOT_PREFIX and MAMBA_EXE manually.')
    MAMBA_ROOT_PREFIX, MAMBA_EXE = input('MAMBA_ROOT_PREFIX: '), input('MAMBA_EXE: ')
    if not os.path.exists(MAMBA_EXE):
        print('Invalid path! Please input valid path.')
        sys.exit(3)


def resolve_micromamba_env_entry():
    res = True if fetch_prefix_from_ps_init() else False
    manually_input_path_wizard() if not res else None


def generate_bat_file():
    python_list = ["python", "python3", "python2"]
    python_path = next((os.getenv(env) for env in python_list if os.getenv(env)), sys.executable)
    bat_file = 'conda.bat'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mamba_path = os.path.dirname(MAMBA_EXE)
    micromamba_bat_path = os.path.join(MAMBA_ROOT_PREFIX, 'condabin', 'micromamba.bat')
    with open(bat_file, 'w', encoding="utf-8") as f:
        f.write('@echo off\n')
        f.write('@set PATH=%PATH%;{}\n'.format(mamba_path))
        f.write('@CALL "{}" >nul 2>&1\n'.format(micromamba_bat_path))
        f.write('"{}" "{}" %*'.format(python_path, os.path.join(current_dir, 'conda')))
    print('Successfully Generated micromamba.bat at {}'.format(os.path.abspath(bat_file)))


if __name__ == '__main__':
    check_platform()
    resolve_micromamba_env_entry()
    generate_bat_file()
