import os
import sys
import platform
import subprocess

import pytest


@pytest.fixture(autouse=True)
def setup_path():
    os.remove("conda.bat") if os.path.exists("conda.bat") else None


@pytest.fixture(scope="session")
def get_env():
    mamba_root_prefix = os.getenv('MAMBA_ROOT_PREFIX_PYTEST', None)
    mamba_exe = os.getenv('MAMBA_EXE_PYTEST', None)
    return mamba_root_prefix, mamba_exe


def call_generate_bat_file(mamba_root_prefix, mamba_exe):
    script_path = os.path.abspath("generate_bat_file.py")
    if platform.system() == 'Windows':
        command = r'cmd /c {} {}'.format(sys.executable, script_path)
    else:
        command = "{} {}".format(sys.executable, script_path)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, shell=True)
    _in = "{}\n{}".format(mamba_root_prefix, mamba_exe)
    print(_in)
    stdout_data, stderr_data = process.communicate(input=_in.encode())
    print(process.returncode, stdout_data, stderr_data)
    return process.returncode


def test_generate_bat_file(get_env):
    mamba_root_prefix, mamba_exe = get_env
    exit_code = call_generate_bat_file(mamba_root_prefix, mamba_exe)
    # Normally
    if platform.system() == 'Windows':
        assert exit_code == 0
        assert os.path.exists("conda.bat")
    # Other platform
    if platform.system() != 'Windows':
        assert exit_code == 2
        assert not os.path.exists("conda.bat")


def test_input_wizard_check(get_env):
    if call_generate_bat_file(None, None) == 0:
        pytest.skip("Only test if the script cannot automatically run!")
    mamba_root_prefix, mamba_exe = get_env
    if mamba_root_prefix and mamba_exe:
        exit_code_1 = call_generate_bat_file(None, None)
        assert exit_code_1 == 3
        assert not os.path.exists("conda.bat")
        exit_code_2 = call_generate_bat_file(mamba_root_prefix, mamba_exe)
        assert exit_code_2 == 0
        assert os.path.exists("conda.bat")
    else:
        pytest.skip("Only available test in manually set mamba_root_prefix and mamba_exe!")

