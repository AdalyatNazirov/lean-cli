# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from unittest import mock

import pytest

from lean.components.config.lean_config_manager import LeanConfigManager
from lean.components.config.project_config_manager import ProjectConfigManager
from lean.components.config.storage import Storage
from lean.models.config import DebuggingMethod
from tests.test_helpers import create_fake_lean_cli_project


def test_get_lean_config_path_returns_closest_config_file() -> None:
    lean_config_path = Path.cwd() / "lean.json"
    cwd_path = Path.cwd() / "sub1" / "sub2" / "sub3"

    lean_config_path.touch()
    cwd_path.mkdir(parents=True)
    os.chdir(cwd_path)

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())

    assert manager.get_lean_config_path() == lean_config_path


def test_get_lean_config_path_raises_error_when_no_config_file_exists() -> None:
    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())

    with pytest.raises(Exception):
        manager.get_lean_config_path()


def test_get_lean_config_path_returns_default_path_when_set() -> None:
    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    manager.set_default_lean_config_path(Path.cwd() / "custom-lean.json")

    assert manager.get_lean_config_path() == Path.cwd() / "custom-lean.json"


def test_get_cli_root_directory_returns_path_to_directory_containing_config_file() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())

    assert manager.get_cli_root_directory() == Path.cwd()


def test_get_data_directory_returns_path_to_data_directory_as_configured_in_config() -> None:
    with (Path.cwd() / "lean.json").open("w+") as file:
        file.write('{ "data-folder": "sub1/sub2/sub3/data" }')

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())

    assert manager.get_data_directory() == Path.cwd() / "sub1" / "sub2" / "sub3" / "data"


def test_get_data_directory_returns_path_to_data_directory_when_config_contains_comments() -> None:
    with (Path.cwd() / "lean.json").open("w+") as file:
        file.write("""
{
    // some comment about the data-folder
    "data-folder": "sub1/sub2/sub3/data"
}
        """)

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())

    assert manager.get_data_directory() == Path.cwd() / "sub1" / "sub2" / "sub3" / "data"


def test_clean_lean_config_removes_auto_configurable_keys_from_original_config() -> None:
    original_config = """
{
    // this configuration file works by first loading all top-level
    // configuration items and then will load the specified environment
    // on top, this provides a layering affect.environment names can be
    // anything, and just require definition in this file.There's
    // two predefined environments, 'backtesting' and 'live', feel free
    // to add more!

    "environment": "backtesting", // "live-paper", "backtesting", "live-interactive", "live-interactive-iqfeed"

    // algorithm class selector
    "algorithm-type-name": "BasicTemplateFrameworkAlgorithm",

    // Algorithm language selector - options CSharp, Python
    "algorithm-language": "CSharp",

    //Physical DLL location
    "algorithm-location": "QuantConnect.Algorithm.CSharp.dll",
    //"algorithm-location": "../../../Algorithm.Python/BasicTemplateFrameworkAlgorithm.py",

    //Research notebook
    //"composer-dll-directory": ".",

    // engine
    "data-folder": "../../../Data/",

    // debugging configuration - options for debugging-method LocalCmdLine, VisualStudio, PTVSD, PyCharm
    "debugging": false,
    "debugging-method": "LocalCmdline",

    // parameters to set in the algorithm (the below are just samples)
    "parameters": {
        // Intrinio account user and password
        "intrinio-username": "",
        "intrinio-password": "",

        "ema-fast": 10,
        "ema-slow": 20
    },

    // handlers
    "log-handler": "QuantConnect.Logging.CompositeLogHandler",
    "messaging-handler": "QuantConnect.Messaging.Messaging",
    "job-queue-handler": "QuantConnect.Queues.JobQueue"
}
    """

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    clean_config = manager.clean_lean_config(original_config)

    for key in ["environment",
                "algorithm-type-name", "algorithm-language", "algorithm-location",
                "composer-dll-directory",
                "debugging", "debugging-method",
                "parameters", "intrinio-username", "intrinio-password", "ema-fast", "ema-slow"]:
        assert f'"{key}"' not in clean_config

    for key in ["data-folder", "log-handler", "messaging-handler", "job-queue-handler"]:
        assert f'"{key}"' in clean_config


def test_clean_lean_config_removes_documentation_of_removed_keys() -> None:
    original_config = """
{
    // this configuration file works by first loading all top-level
    // configuration items and then will load the specified environment
    // on top, this provides a layering affect.environment names can be
    // anything, and just require definition in this file.There's
    // two predefined environments, 'backtesting' and 'live', feel free
    // to add more!

    "environment": "backtesting", // "live-paper", "backtesting", "live-interactive", "live-interactive-iqfeed"

    // algorithm class selector
    "algorithm-type-name": "BasicTemplateFrameworkAlgorithm",

    // Algorithm language selector - options CSharp, Python
    "algorithm-language": "CSharp",

    //Physical DLL location
    "algorithm-location": "QuantConnect.Algorithm.CSharp.dll",
    //"algorithm-location": "../../../Algorithm.Python/BasicTemplateFrameworkAlgorithm.py",

    //Research notebook
    //"composer-dll-directory": ".",

    // engine
    "data-folder": "../../../Data/",

    // debugging configuration - options for debugging-method LocalCmdLine, VisualStudio, PTVSD, PyCharm
    "debugging": false,
    "debugging-method": "LocalCmdline",

    // parameters to set in the algorithm (the below are just samples)
    "parameters": {
        // Intrinio account user and password
        "intrinio-username": "",
        "intrinio-password": "",

        "ema-fast": 10,
        "ema-slow": 20
    },

    // handlers
    "log-handler": "QuantConnect.Logging.CompositeLogHandler",
    "messaging-handler": "QuantConnect.Messaging.Messaging",
    "job-queue-handler": "QuantConnect.Queues.JobQueue"
}
    """

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    clean_config = manager.clean_lean_config(original_config)

    assert "// algorithm class selector" not in clean_config
    assert "// Algorithm language selector - options CSharp, Python" not in clean_config
    assert "//Physical DLL location" not in clean_config
    assert "//Research notebook" not in clean_config
    assert "// debugging configuration - options for debugging-method LocalCmdLine, VisualStudio, PTVSD, PyCharm" not in clean_config
    assert "// parameters to set in the algorithm (the below are just samples)" not in clean_config
    assert "// Intrinio account user and password" not in clean_config

    assert "// engine" in clean_config
    assert "// handlers" in clean_config


def test_get_complete_lean_config_returns_dict_with_all_keys_removed_in_clean_lean_config() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("backtesting", Path.cwd() / "Python Project" / "main.py", None)

    for key in ["environment",
                "algorithm-type-name", "algorithm-language", "algorithm-location",
                "composer-dll-directory",
                "debugging", "debugging-method",
                "parameters"]:
        assert key in config


def test_get_complete_lean_config_sets_environment() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert config["environment"] == "my-environment"


def test_get_complete_lean_config_sets_close_automatically() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert config["close-automatically"]


def test_get_complete_lean_config_disables_debugging_when_no_method_given() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert not config["debugging"]


@pytest.mark.parametrize("method,value", [(DebuggingMethod.PyCharm, "PyCharm"),
                                          (DebuggingMethod.PTVSD, "PTVSD"),
                                          (DebuggingMethod.Mono, "LocalCmdline")])
def test_get_complete_lean_config_enables_debugging_when_method_given(method: DebuggingMethod, value: str) -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", method)

    assert config["debugging"]
    assert config["debugging-method"] == value


def test_get_complete_lean_config_sets_credentials_from_cli_config_manager() -> None:
    create_fake_lean_cli_project()

    cli_config_manager = mock.Mock()
    cli_config_manager.user_id.get_value.return_value = "123"
    cli_config_manager.api_token.get_value.return_value = "456"

    manager = LeanConfigManager(cli_config_manager, ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert config["job-user-id"] == "123"
    assert config["api-access-token"] == "456"


def test_get_complete_lean_config_sets_python_algorithm_details() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert config["algorithm-type-name"] == "main"
    assert config["algorithm-language"] == "Python"
    assert config["algorithm-location"] == "/LeanCLI/Python Project/main.py"


def test_get_complete_lean_config_sets_csharp_algorithm_details() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "CSharp Project" / "Main.cs", None)

    assert config["algorithm-type-name"] == "CSharpProject"
    assert config["algorithm-language"] == "CSharp"
    assert config["algorithm-location"] == "LeanCLI.dll"


def test_get_complete_lean_config_sets_parameters() -> None:
    create_fake_lean_cli_project()

    Storage(str(Path.cwd() / "Python Project" / "config.json")).set("parameters", {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    })

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_complete_lean_config("my-environment", Path.cwd() / "Python Project" / "main.py", None)

    assert config["parameters"] == {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }


def test_get_lean_config_returns_contents_of_lean_config_file_as_dict() -> None:
    create_fake_lean_cli_project()

    manager = LeanConfigManager(mock.Mock(), ProjectConfigManager())
    config = manager.get_lean_config()

    assert config == {"data-folder": "data"}
