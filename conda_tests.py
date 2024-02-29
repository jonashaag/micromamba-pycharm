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


def run_conda(args, use_bat):
    print("use_bat: ", use_bat)
    executable = ["cmd", "/c"] if (use_bat and SYSTEM == 'Windows') else [sys.executable]
    exec_file = "conda.bat" if (use_bat and SYSTEM == 'Windows') else "conda"
    commend = executable + [exec_file] + args
    if use_bat and SYSTEM == 'Windows':
        call_generate_bat_file(None, None)
    if use_bat and SYSTEM != 'Windows':
        pytest.skip("use_bat test only available in Windows!")
    return (
        subprocess.check_output(commend)
        .decode(locale.getpreferredencoding())
        .rstrip()
    )


@pytest.fixture(autouse=True)
@pytest.mark.parametrize("use_bat", [False, True])
def setup_PATH(monkeypatch, use_bat):
    monkeypatch.setenv("PATH", os.getcwd() + (":" if SYSTEM != 'Windows' else ';') + os.environ["PATH"])
    run_conda(["self-check"], use_bat)


@pytest.mark.parametrize("use_bat", [False, True])
def test_info_envs_json(use_bat):
    result = run_conda(["info", "--envs", "--json"], use_bat)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"envs_dirs", "conda_prefix", "envs"}
    assert isinstance(data["envs_dirs"], list)
    assert all(isinstance(item, unicode) for item in data["envs_dirs"])
    assert isinstance(data["conda_prefix"], unicode)
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, unicode) for item in data["envs"])


@pytest.mark.parametrize("use_bat", [False, True])
def test_env_list_json(use_bat):
    result = run_conda(["env", "list", "--json"], use_bat)
    data = json.loads(result)
    assert isinstance(data, dict)
    assert set(data.keys()) == {"envs"}
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, unicode) for item in data["envs"])


@pytest.mark.parametrize("use_bat", [False, True])
def test_list(use_bat):
    result = run_conda(["list", "-n", "base"], use_bat)
    result_e = run_conda(["list", "-n", "base", "-e"], use_bat)
    ref = subprocess.check_output(["micromamba", "list", "-n", "base"]).strip()
    ref = "\n".join(l.strip() for l in ref.splitlines()[4:])
    assert result == ref
    assert result_e == "\n".join("=".join(l.split()[:-1]) for l in ref.splitlines())


@pytest.mark.parametrize("use_bat", [False, True])
def test_run(use_bat):
    assert "42" == run_conda(["run", "echo", "42"], use_bat)
    assert "42" == run_conda(["run", "--no-capture-output", "echo", "42"], use_bat)


@pytest.mark.parametrize("use_bat", [False, True])
def test_create(tmp_path, use_bat):
    run_conda(["create", "-p", str(tmp_path / "env")], use_bat)
    run_conda(["install", "-p", str(tmp_path / "env"), "xtensor"], use_bat)
