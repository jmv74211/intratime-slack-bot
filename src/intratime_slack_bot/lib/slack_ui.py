from intratime_slack_bot.lib import slack

# ----------------------------------------------------------------------------------------------------------------------


def get_clock_ui():
    return {
        "title": "Intratime: Clocking",
        "submit_label": "Submit",
        "callback_id": "clock",
        "elements": [
            {
                "label": "Action",
                "type": "select",
                "name": "action",
                "options": [
                    {
                        "label": "IN",
                        "value": "in"
                    },
                    {
                        "label": "PAUSE",
                        "value": "pause"
                    },
                    {
                        "label": "RETURN",
                        "value": "return"
                    },
                    {
                        "label": "OUT",
                        "value": "out"
                    }
                ]
            }
        ]
    }

# ----------------------------------------------------------------------------------------------------------------------


def get_sign_up_ui():
    return {
        "title": "Intratime: Sign up",
        "submit_label": "Submit",
        "callback_id": "sign_up",
        "elements": [
            {
                "label": "Intratime email",
                "name": "email",
                "type": "text",
                "subtype": "email",
                "placeholder": "you@example.com"
            },
            {
                "label": "Intratime password",
                "name": "password",
                "type": "text",
                "placeholder": "password",
                "hint": "Attention: There is no password field type, so it will be written in plain text"
            }
        ]
    }

# ----------------------------------------------------------------------------------------------------------------------


def get_update_user_ui():
    return {
        "title": "Intratime: Update user",
        "submit_label": "Submit",
        "callback_id": "update_user",
        "elements": [
            {
                "label": "Email Address",
                "name": "email",
                "type": "text",
                "subtype": "email",
                "placeholder": "you@example.com"
            },
            {
                "label": "Password",
                "name": "password",
                "type": "text",
                "placeholder": "password",
                "hint": "Attention: There is no password field type, so it will be written in plain text"

            }
        ]
    }

# ----------------------------------------------------------------------------------------------------------------------


def get_delete_user_ui():
    return {
        "title": "Intratime: Delete user",
        "submit_label": "Submit",
        "callback_id": "delete_user",
        "elements": [
            {
                "label": "Are you sure you want to delete your user?",
                "type": "select",
                "name": "delete",
                "options": [
                    {
                        "label": "No",
                        "value": "no"
                    },
                    {
                        "label": "Yes",
                        "value": "yes"
                    }
                ]
            }
        ]
    }

# ----------------------------------------------------------------------------------------------------------------------


def get_user_history_ui(callback_id):
    title_action = 'Clock'

    if callback_id == slack.TIME_HISTORY_CALLBACK:
        title_action = 'Time'

    return {
        "title": f"Intratime: {title_action} history",
        "submit_label": "Submit",
        "callback_id": callback_id,
        "elements": [
            {
                "label": "Select the time range",
                "type": "select",
                "name": "action",
                "options": [
                    {
                        "label": "Today history",
                        "value": "today_history"
                    },
                    {
                        "label": "Week history",
                        "value": "week_history"
                    },
                    {
                        "label": "Month history",
                        "value": "month_history"
                    }
                ]
            }
        ]
    }

# ----------------------------------------------------------------------------------------------------------------------


def get_user_worked_time_ui():
    return {
        "title": "Intratime: Worked time",
        "submit_label": "Submit",
        "callback_id": "user_worked_time",
        "elements": [
            {
                "label": "Select the time range",
                "type": "select",
                "name": "action",
                "options": [
                    {
                        "label": "Today hours",
                        "value": "today_hours"
                    },
                    {
                        "label": "Week hours",
                        "value": "week_hours"
                    },
                    {
                        "label": "Month hours",
                        "value": "month_hours"
                    }
                ]
            }
        ]
    }
