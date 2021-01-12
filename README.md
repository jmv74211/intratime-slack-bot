# Intratime slack app

![Status](https://img.shields.io/badge/Version-2.0-blue.svg)
![Status](https://img.shields.io/badge/Status-stable-green.svg)

Application to clock in intratime app using using slack.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/intratime_slack_app_logo.png">
</p>


# Introduction

Intratime slack app is an application that allows you to clock in the [Intratime](https://www.intratime.es/)
application using the slack client and get this related info.

You only need to enter your intratime credentials (they will be stored in an encrypted database) and write a single
command to clock your actions or get information about them.

This application has the following capabilities:

- Clock your entry, pause, return or out action.
- Get your total worked time (clocked).
- Get your clock history.
- Get your worked time history.

---

# How to use

## Considerations before starting

- All messages generated as a result of any command are of **private visibility**, thus avoiding flooding public
conversations and preventing the rest of the users from seeing your information or actions.

- When the account is created using the intratime credentials, the **password is stored in encrypted form**.

- **Requests and slack content** to the server (where the application is running) **are encrypted**. (This encryption is
external to the application, using NGINX as reverse proxy).

- The _intratime-bot_ service will **only deal with requests made by slack**, using a signature key. This prevents
unwanted access in external applications.

- **Most commands can be launched via user interface or directly with parameters**. Commands without parameters will
activate the GUI. See the `/help` command for more information available command parameters.

## User management

**Register your app user**

First of all, it is necessary to have an intratime and slack account. From here, we will have to sign up in this app
using the `/sign_up` command in the slack chat and then introducing **your intratime credentials** in the related
fields.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/sign_up.png">
</p>

>**Note**: There are no password type fields, so the password will be written in raw in the field. Be careful with this.

**Update your app user**

If you have ever modified your credentials in intratime (in the intratime application), then you will need to
update your credentials in this app as well, to do so use the `/update_user` command and enter your new credentials:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/update_user.png">
</p>

**Delete your app user**

In case you want to delete your user in this app, you can do it with the command `/delete_user`.

## Clock your actions

Once the user is registered (you only need to do it once), you can clock your action (_IN_, _PAUSE_, _RETURN_ or _OUT_)
in the intratime application using the `/clock` command.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/clocking.png">
</p>

It is also possible to activate this command directly by passing it one of the following actions: _IN_, _PAUSE_,
_RETURN_  _OUT_.

```
/clock <action>
```

If the action is successful, the following message will be displayed:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/clock_example.png">
</p>

This functionality also filters out possible inconsistent clockings, such as trying to clock a _RETURN_ without a
previous _PAUSE_. In this case, we can see messages like the following:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/bad_clock_action_example.png">
</p>

## Check your total worked time

A very useful feature is to check how long we have been working, making the calculation based on the clockings we
have made. We can do this calculation on a daily, weekly or monthly basis.

For this you can use the `/time` command.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/worked_time.png">
</p>

It is also possible to activate this command directly by passing it one of the following parameters: _today_, _week_,
_month_.

```
/time <parameter>
```

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/worked_time_example.png">
</p>

## Check your clock history

Do you need to check the clocks made? This command shows you all the information of the clockings made in the current
day, week or month.

For this you can use the `/clock_history` command.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/clock_history.png">
</p>

It is also possible to activate this command directly by passing it one of the following parameters:  _today_, _week_,
_month_.

```
/clock_history <parameter>
```

>**Note**: This information will be shown in the private conversation that each user has with the slack application.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/clock_history_example.png">
</p>


## Check your worked time history

Do you want to know how many hours you worked each day? This commands shows you a list of time worked for each day in
the specified range, on the current day, week or month.

For this you can use the `/time_history` command.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/time_history.png">
</p>

It is also possible to activate this command directly by passing it one of the following parameters:  _today_, _week_,
_month_.

```
/time_history <parameter>
```

>**Note**: This information will be shown in the private conversation that each user has with the slack application.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/worked_time_history_example.png">
</p>


## Check your current day summary

If you want to get a summary of the time worked and clockings made today, you can use directly the `/today` command.
This command has not parameters.

```
/today
```

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/today_summary.png">
</p>

## Get help info

In case you need information about the available commands and parameters, you can run the command `/help`, to
display the following help menu:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/help.png">
</p>

---

# App components

This application consists of the following services:

- **intratime-bot**: Main service that attends to all slack requests and communicates with the rest of services and
components to carry out the request.

- **mongo-service**: Storage and database service.

- **mongo-express**: Service to visualize and make queries in a graphic way in the database service.

The implemented structure can be seen in the following figure:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/readme/app_components.png">
</p>

---

# How to deploy

## Configure your slack app

First you will have to create a slack application. You can create one from this website
[https://api.slack.com/](https://api.slack.com/).


**Get slack app credentials**

Once created, you will have to obtain your **app tokens**. You can find it in `OAuth & Permissions section`.
It will have a format like the following:

_OAuth Access Token_
```
xoxp-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
```

_Bot User OAuth Access Token_

```
xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
```

It will also be necessary to obtain the **signing secret key** to verify that the requests come from our slack app. You
can find this key in _Basic information_ section.

**Set your token scopes**

A Slack app's capabilities and permissions are governed by the scopes it requests. You can configure them in
 _OAuth & Permissions_ section. The current token scopes are as follows:

- **Bot token scopes**: _channels:history_, _commands_, _groups:history_
- **User Token Scopes**: _chat:write_

**Set your interactivity endpoint**

All the interactions with the graphic slack components (in this case the modal windows and forms are used) have to be
attended from a specific endpoint.

This endpoint belongs to the _intratime-bot_ service with the `/interactive` URI , so it will be necessary to indicate
in the _Interactivity & Shortcuts_ section the _Request URL_ for this endpoint. For example:

```
https://<domain_name>/interactive
```

**Define your commands**

Commands enable users to interact with your app from within Slack. In this case, we have to define the following
commands:

- `/sign_up`: _https://<domain_name>/sign\_up_
- `/clock`: _https://<domain_name>/clock_
- `/update_user`: _https://<domain_name>/update\_user_
- `/delete_user`: _https://<domain_name>/delete\_user_
- `/clock_history`: _https://<domain_name>/clock\_history_
- `/time`: _https://<domain_name>/time_
- `/time_history`: _https://<domain_name>/time\_history_
- `/today`: _https://<domain_name>/today_
- `/help`: _https://<domain_name>/help_

## Configure your app settings

You have to configure the intratime slack bot application modifying the
[settings.py](https://github.com/jmv74211/intratime-slack-bot/blob/master/src/intratime_slack_bot/config/settings.py)
file.

In addition, you have to update the [.env](https://github.com/jmv74211/intratime-slack-bot/blob/master/.env) file
to enter your _mongo_ and _mongo-express_ credentials.

In case of modifying default ports ..., take a look at the
[docker-compose.yaml](https://github.com/jmv74211/intratime-slack-bot/blob/master/docker-compose.yaml) file
and update to your new values.

## Run the app

Once the application is configured (see the previous steps), Running the application is very simple, you just need
to have installed [docker](https://www.docker.com/get-started) and
[docker-compose](https://docs.docker.com/compose/install/), and execute the following command in root directory.

```bash
docker-compose build && docker-compose up
```

All services will be automatically started.

You can check if the configuration and deployment has been done correctly by running the
[unit](https://github.com/jmv74211/intratime-slack-bot/tree/master/test/unit) and
[integration tests](https://github.com/jmv74211/intratime-slack-bot/tree/master/test/integration).

>**Note**: The unit and integration tests must be run separately

You can run these tests with `pytest` module. For example, inside `test/unit` folder, we can run:

```
pytest -v --tb=short .
```

The same process must be done to launch the integration tests.

---

# Contributions

Any doubt or suggestion, you can create issues and/or make pull requests :)
