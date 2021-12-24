import pytest

from clockzy.lib.models.clock import Clock
from clockzy.lib.test_framework.database import item_exists, intratime_user_parameters, clock_parameters
from clockzy.lib.db.db_schema import CLOCK_TABLE


# Pytest tierdown fixture is executed from righ to left position
@pytest.mark.parametrize('user_parameters, clock_parameters', [(intratime_user_parameters, clock_parameters)])
def test_save_clock(add_pre_user, delete_post_user, delete_post_clock):
    test_clock = Clock(**clock_parameters)

    # Add the clock and check that 1 row has been affected (no exception when running)
    test_clock.save()
    clock_parameters['id'] = test_clock.id

    # Query and check that the clock exist
    assert item_exists({'id': test_clock.id}, CLOCK_TABLE)


@pytest.mark.parametrize('user_parameters, clock_parameters', [(intratime_user_parameters, clock_parameters)])
def test_update_clock(add_pre_user, add_pre_clock, delete_post_user, delete_post_clock):
    test_clock = Clock(**clock_parameters)
    test_clock.id = add_pre_clock
    clock_parameters['id'] = test_clock.id

    # Update the clock info and check that 1 row has been affected (no exception when running)
    test_clock.action = 'OUT'
    test_clock.update()

    # Query and check that the clock exist
    assert item_exists({'id': test_clock.id, 'action': 'OUT'}, CLOCK_TABLE)


@pytest.mark.parametrize('user_parameters, clock_parameters', [(intratime_user_parameters, clock_parameters)])
def test_delete_clock(add_pre_user, add_pre_clock, delete_post_user):
    test_clock = Clock(**clock_parameters)
    test_clock.id = add_pre_clock
    clock_parameters['id'] = test_clock.id

    # Delete the clock info and check that 1 row has been affected (no exception when running)
    test_clock.delete()

    # Query and check that the clock does not exist
    assert not item_exists({'id': test_clock.id}, CLOCK_TABLE)
