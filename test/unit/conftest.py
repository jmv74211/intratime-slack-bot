import pytest

from clockzy.lib.models.user import User
from clockzy.lib.models.clock import Clock
from clockzy.lib.models.command_history import CommandHistory
from clockzy.lib.models.config import Config
from clockzy.lib.models.alias import Alias
from time import sleep


@pytest.fixture
def delete_post_user(user_parameters):
    yield
    user = User(**user_parameters)
    user.delete()


@pytest.fixture
def add_pre_user(user_parameters):
    user = User(**user_parameters)
    user.save()
    yield


@pytest.fixture
def delete_post_clock(clock_parameters):
    yield
    clock_id = clock_parameters['id']
    del clock_parameters['id']
    clock = Clock(**clock_parameters)
    clock.id = clock_id
    clock.delete()


@pytest.fixture
def add_pre_clock(clock_parameters):
    clock = Clock(**clock_parameters)
    clock.save()
    yield clock.id


@pytest.fixture
def delete_post_command_history(command_history_parameters):
    yield
    command_history_id = command_history_parameters['id']
    del command_history_parameters['id']
    command_history = CommandHistory(**command_history_parameters)
    command_history.id = command_history_id
    command_history.delete()


@pytest.fixture
def add_pre_command_history(command_history_parameters):
    command_history = CommandHistory(**command_history_parameters)
    command_history.save()
    yield command_history.id


@pytest.fixture
def delete_post_config(config_parameters):
    yield
    config = Config(**config_parameters)
    config.delete()


@pytest.fixture
def add_pre_config(config_parameters):
    config = Config(**config_parameters)
    config.save()
    yield


@pytest.fixture
def delete_post_alias(alias_parameters):
    yield
    alias = Alias(**alias_parameters)
    alias.delete()


@pytest.fixture
def add_pre_alias(alias_parameters):
    alias = Alias(**alias_parameters)
    alias.save()
    yield
