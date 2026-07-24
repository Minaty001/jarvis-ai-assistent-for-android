"""Tests for the intent classifier."""

import pytest
from jarvis.core.intent import classify_intent


class TestIntentClassifier:
    """Verify rule-based intent matching and parameter extraction."""

    def test_open_app_intent(self):
        intent, params = classify_intent("open calculator")
        assert intent == "open_app"
        assert params["app_name"] == "calculator"

    def test_open_settings_intent(self):
        intent, params = classify_intent("open settings")
        assert intent == "open_settings"

    def test_tell_time_intent(self):
        intent, params = classify_intent("what's the time")
        assert intent == "tell_time"

    def test_tell_date_intent(self):
        intent, params = classify_intent("what is the date")
        assert intent == "tell_date"

    def test_battery_status(self):
        intent, params = classify_intent("battery status")
        assert intent == "battery_status"

    def test_flashlight_on(self):
        intent, params = classify_intent("turn on flashlight")
        assert intent == "flashlight_on"

    def test_flashlight_off(self):
        intent, params = classify_intent("disable flashlight")
        assert intent == "flashlight_off"

    def test_volume_up(self):
        intent, params = classify_intent("volume up")
        assert intent == "volume_up"

    def test_volume_down(self):
        intent, params = classify_intent("lower volume")
        assert intent == "volume_down"

    def test_set_volume(self):
        intent, params = classify_intent("set volume to 7")
        assert intent == "set_volume"
        assert params["level"] == "7"

    def test_brightness_up(self):
        intent, params = classify_intent("increase brightness")
        assert intent == "brightness_up"

    def test_set_brightness(self):
        intent, params = classify_intent("set brightness to 50")
        assert intent == "set_brightness"
        assert params["level"] == "50"

    def test_wifi_on(self):
        intent, params = classify_intent("turn on wifi")
        assert intent == "wifi_on"

    def test_wifi_off(self):
        intent, params = classify_intent("wifi off")
        assert intent == "wifi_off"

    def test_bluetooth_on(self):
        intent, params = classify_intent("enable bluetooth")
        assert intent == "bluetooth_on"

    def test_search_google(self):
        intent, params = classify_intent("search for Python tutorials")
        assert intent == "search_google"
        assert "python tutorials" in params["query"]

    def test_take_note(self):
        intent, params = classify_intent("take a note that I need milk")
        assert intent == "take_note"
        assert "i need milk" in params["content"]

    def test_read_notes(self):
        intent, params = classify_intent("show my notes")
        assert intent == "read_notes"

    def test_set_reminder(self):
        intent, params = classify_intent("set a reminder to call John")
        assert intent == "set_reminder"
        assert "call john" in params["text"]

    def test_remember_fact(self):
        intent, params = classify_intent("remember that my favorite color is blue")
        assert intent == "remember_fact"

    def test_exit_intent(self):
        intent, params = classify_intent("goodbye")
        assert intent == "exit"

    def test_general_chat_fallback(self):
        intent, params = classify_intent("tell me a joke")
        assert intent == "general_chat"
        assert params["text"] == "tell me a joke"

    def test_go_home(self):
        intent, params = classify_intent("go home")
        assert intent == "go_home"

    def test_show_notifications(self):
        intent, params = classify_intent("show notifications")
        assert intent == "show_notifications"
