import json
import os
import subprocess

import pytest


def run_conda(args):
    return subprocess.check_output(["conda"] + args, text=True).rstrip()


@pytest.fixture(autouse=True)
def setup_PATH(monkeypatch):
    monkeypatch.setenv("PATH", os.getcwd() + ":" + os.environ["PATH"])
    run_conda(["self-check"])


def test_info_envs_json():
    result = run_conda(["info", "--envs", "--json"])
    data = json.loads(result)
    assert isinstance(data, dict)
    assert data.keys() == {"envs_dirs", "conda_prefix", "envs"}
    assert isinstance(data["envs_dirs"], list)
    assert all(isinstance(item, str) for item in data["envs_dirs"])
    assert isinstance(data["conda_prefix"], str)
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, str) for item in data["envs"])


def test_env_list_json():
    result = run_conda(["env", "list", "--json"])
    data = json.loads(result)
    assert isinstance(data, dict)
    assert data.keys() == {"envs"}
    assert isinstance(data["envs"], list)
    assert all(isinstance(item, str) for item in data["envs"])


def test_list():
    result = run_conda(["list", "-n", "base"])
    result_e = run_conda(["list", "-n", "base", "-e"])
    ref = subprocess.check_output(
        ["micromamba", "list", "-n", "base"], text=True
    ).strip()
    ref = "\n".join(l.strip() for l in ref.splitlines()[4:])
    assert result == ref
    assert result_e == "\n".join("=".join(l.split()[:-1]) for l in ref.splitlines())


def test_run():
    assert "42" == run_conda(["run", "echo", "42"])
    assert "42" == run_conda(["run", "--no-capture-output", "echo", "42"])


def test_create(tmp_path):
    run_conda(["create", "-p", tmp_path / "env"])
    run_conda(["install", "-p", tmp_path / "env", "xtensor"])
