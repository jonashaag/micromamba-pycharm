import json
import locale
import os
import platform
import subprocess
import sys

import pytest
from generate_bat_file_tests import call_generate_bat_file

try:
    unicode  # noqa
except NameError:
    unicode = str

SYSTEM = platform.system()


def run_conda(args, test_platform):
    executable = ["cmd", "/c"] if SYSTEM == 'Windows' else [sys.executable]
    exec_file = "conda.bat" if SYSTEM == 'Windows' else "conda"
    commend = executable + [exec_file] + args
    if_windows = SYSTEM == 'Windows'
    if_unix = SYSTEM in ("Linux", "Darwin")
    if test_platform == 'Windows' and if_windows:
        call_generate_bat_file(None, None)
    if (test_platform == 'Windows' and if_unix) or (test_platform != 'Windows' and if_windows):
        pytest.skip("The expected test platform {} is inconsistent with the current test platform {}, "
                    "skip the test").format(test_platform, SYSTEM)
    return (
        subprocess.check_output(commend)
        .decode(locale.getpreferredencoding())
        .rstrip()
    )


@pytest.fixture(autouse=True)
@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def setup_PATH(monkeypatch, test_platform):
    monkeypatch.setenv("PATH", os.getcwd() + (":" if SYSTEM != 'Windows' else ';') + os.environ["PATH"])
    run_conda(["self-check"], test_platform)


@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def test_info_envs_json(test_platform):
    result = run_conda(["info", "--envs", "--json"], test_platform)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"envs_dirs", "conda_prefix", "envs"}
    assert isinstance(data["envs_dirs"], list)
    assert all(isinstance(item, unicode) for item in data["envs_dirs"])
    assert isinstance(data["conda_prefix"], unicode)
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, unicode) for item in data["envs"])


@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def test_env_list_json(test_platform):
    result = run_conda(["env", "list", "--json"], test_platform)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"envs"}
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, unicode) for item in data["envs"])


@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def test_list(test_platform):
    result = run_conda(["list", "-n", "base"], test_platform)
    result_e = run_conda(["list", "-n", "base", "-e"], test_platform)
    ref = subprocess.check_output(["micromamba", "list", "-n", "base"]).strip()
    ref = "\n".join(l.strip() for l in ref.splitlines()[4:])
    assert result == ref
    assert result_e == "\n".join("=".join(l.split()[:-1]) for l in ref.splitlines())


@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def test_run(test_platform):
    assert "42" == run_conda(["run", "echo", "42"], test_platform)
    assert "42" == run_conda(["run", "--no-capture-output", "echo", "42"], test_platform)


@pytest.mark.parametrize("test_platform", ["Windows", "Unix"])
def test_create(tmp_path, test_platform):
    run_conda(["create", "-p", str(tmp_path / "env")], test_platform)
    run_conda(["install", "-p", str(tmp_path / "env"), "xtensor"], test_platform)
