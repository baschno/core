"""Test reproduce state for Logitech Harmony Hub."""
from homeassistant.core import State

from tests.common import async_mock_service


async def test_reproducing_states(hass, caplog):
    """Test reproducing Logitech Harmony Hub states."""
    hass.states.async_set("harmony.entity_off", "off", {})
    hass.states.async_set("harmony.entity_on", "on", {"color": "red"})

    turn_on_calls = async_mock_service(hass, "harmony", "turn_on")
    turn_off_calls = async_mock_service(hass, "harmony", "turn_off")

    # These calls should do nothing as entities already in desired state
    await hass.helpers.state.async_reproduce_state(
        [
            State("harmony.entity_off", "off"),
            State("harmony.entity_on", "on", {"color": "red"}),
        ],
        blocking=True,
    )

    assert len(turn_on_calls) == 0
    assert len(turn_off_calls) == 0

    # Test invalid state is handled
    await hass.helpers.state.async_reproduce_state(
        [State("harmony.entity_off", "not_supported")], blocking=True
    )

    assert "not_supported" in caplog.text
    assert len(turn_on_calls) == 0
    assert len(turn_off_calls) == 0

    # Make sure correct services are called
    await hass.helpers.state.async_reproduce_state(
        [
            State("harmony.entity_on", "off"),
            State("harmony.entity_off", "on", {"color": "red"}),
            # Should not raise
            State("harmony.non_existing", "on"),
        ],
        blocking=True,
    )

    assert len(turn_on_calls) == 1
    assert turn_on_calls[0].domain == "harmony"
    assert turn_on_calls[0].data == {
        "entity_id": "harmony.entity_off",
        "color": "red",
    }

    assert len(turn_off_calls) == 1
    assert turn_off_calls[0].domain == "harmony"
    assert turn_off_calls[0].data == {"entity_id": "harmony.entity_on"}
