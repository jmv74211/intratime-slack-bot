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
                        "label": "Entry",
                        "value": "in"
                    },
                    {
                        "label": "Pause",
                        "value": "pause"
                    },
                    {
                        "label": "Return",
                        "value": "return"
                    },
                    {
                        "label": "Leave",
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
                "placeholder": "password"
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
                "placeholder": "password"
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
                        "value": "cancel"
                    },
                    {
                        "label": "Yes",
                        "value": "confirm_delete"
                    }
                ]
            }
        ]
    }
