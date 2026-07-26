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

    def test_search_conversation(self):
        intent, params = classify_intent("search my conversation for python")
        assert intent == "search_conversation"
        assert "python" in params["query"]

    def test_search_conversation_alt(self):
        intent, params = classify_intent("what did we talk about python")
        assert intent == "search_conversation"
        assert "python" in params["query"]

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

    def test_export_conversation(self):
        intent, params = classify_intent("export conversation")
        assert intent == "export_conversation"

    def test_export_conversation_alt(self):
        intent, params = classify_intent("save chat history")
        assert intent == "export_conversation"

    def test_export_conversation_backup(self):
        intent, params = classify_intent("backup conversation")
        assert intent == "export_conversation"

    def test_take_screenshot(self):
        intent, params = classify_intent("take a screenshot")
        assert intent == "take_screenshot"

    def test_take_screenshot_short(self):
        intent, params = classify_intent("screenshot")
        assert intent == "take_screenshot"

    def test_capture_screen(self):
        intent, params = classify_intent("capture the screen")
        assert intent == "take_screenshot"

    def test_send_notification(self):
        intent, params = classify_intent("send a notification saying battery low")
        assert intent == "send_notification"
        assert "battery low" in params["content"]

    def test_notify_me(self):
        intent, params = classify_intent("notify me that meeting starts")
        assert intent == "send_notification"
        assert "meeting starts" in params["content"]

    def test_airplane_mode_on(self):
        intent, params = classify_intent("turn on airplane mode")
        assert intent == "airplane_mode"

    def test_airplane_mode_off(self):
        intent, params = classify_intent("disable flight mode")
        assert intent == "airplane_mode"

    def test_airplane_mode_toggle(self):
        intent, params = classify_intent("toggle airplane mode")
        assert intent == "airplane_mode"

    def test_do_not_disturb_on(self):
        intent, params = classify_intent("turn on do not disturb")
        assert intent == "do_not_disturb"

    def test_do_not_disturb_off(self):
        intent, params = classify_intent("disable silent mode")
        assert intent == "do_not_disturb"

    def test_do_not_disturb_toggle(self):
        intent, params = classify_intent("toggle dnd")
        assert intent == "do_not_disturb"

    def test_sensor_data(self):
        intent, params = classify_intent("read sensor data")
        assert intent == "sensor_data"

    def test_sensor_data_specific(self):
        intent, params = classify_intent("sensor readings accelerometer")
        assert intent == "sensor_data"
        assert "accelerometer" in params.get("sensor", "")

    def test_recurring_timer(self):
        intent, params = classify_intent("set a recurring timer for 5 minutes called stand up")
        assert intent == "set_timer"
        assert params["duration"] == "5"
        assert "min" in params.get("unit", "")
        assert "stand up" in params.get("label", "")

    def test_repeat_every_timer(self):
        intent, params = classify_intent("repeat every 30 seconds")
        assert intent == "set_timer"
        assert params["duration"] == "30"
        assert "sec" in params.get("unit", "")

    def test_repeat_every_minutes_label(self):
        intent, params = classify_intent("repeat every 10 minutes called coffee break")
        assert intent == "set_timer"
        assert params["duration"] == "10"
        assert "min" in params.get("unit", "")
        assert "coffee break" in params.get("label", "")
