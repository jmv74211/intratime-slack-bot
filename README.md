# Intratime slack app

![Status](https://img.shields.io/badge/Version-1.0-blue.svg)
![Status](https://img.shields.io/badge/Status-stable-green.svg)

Application to remember and clock through intratime API from slack client.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/intratime_slack_app_logo.png">
</p>

# Introduction

Intratime slack app is an application that allows you to clock your work schedule through the `Intratime` application.

You only need to enter your intratime credentials (they will be stored in an encrypted database) and write a single command to clock your entry, pause, return or exit.

# How to use

**Reminder bot messages**

The reminder bot will process all the messages of the conversations to which it has been added, and will look for a series of [activation patterns](https://github.com/jmv74211/Intratime-slack-bot/blob/master/src/config/trigger_patterns.json) to send a reminder message to clock.

>**Note**: This message will only be visible to the user who has written in the chat.

For example, if we write "buenos días", it will show us the following message:

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/bot_reminder_example.png">
</p>

> **Note**: In this case, the activation patterns are written in Spanish. You can edit it if necessary.

**Register your user**

The first step to be done from the client, is to register our credentials. To do this, you have to execute the defined command to register a user. In this example the command is `/sign_up`.

> **Note**: You will only be able to register with your correct intratime credentials

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/sign_up_command_example.png">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/sign_up_form_example.png">
</p>

**Clocking**

Once the user is registered (you only need to do it once), you can select the type of transfer to make and register it in intratime. To do this, execute the command for this purpose, in this example `/register`.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/register_command_example.png">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/register_form_example.png">
</p>


**Update your intratime credentials**

If you make any changes to your intratime credentials, you must update them in this application as well. To do this, you can type the command for it, in this example `/update_user`.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/update_user_command_example.png">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/update_user_form_example.png">
</p>


**Delete your user from this app**

Finally, if you want to remove your user from the application, you can do so by using the command for that purpose, in this example `/delete`.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/delete_user_command_example.png">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/delete_user_form_example.png">
</p>

# App components

The application is divided into a set of independent microservices that communicate with each other to carry out certain tasks. Each of these microservices is deployed in a separate docker container.

In the following figure, you can see the set of microservices deployed and the communication between them.

<p align="center">
<img src="https://raw.githubusercontent.com/jmv74211/Intratime-slack-bot/master/images/app_architecture.png">
</p>

The objective of each of these components is as follows:

- **Reminder bot**: Service to remind the user to clock in intratime after writing certain patterns in the slack channels.
- **Dialog service**: Service to receive requests for slack commands and open forms in the slack client.
- **User service**: Service for user management.
- **Intratime service**: Service for sending requests to the intratime API.
- **Logger service**: Service to record logs of the rest of the services.
- **MongoDB**: Database service.
- **MongoExpress**: Database Query Interface Service.

# How to deploy

## Configure your slack app

First you will have to create a slack application.You can create one from this website [https://api.slack.com/](https://api.slack.com/).


**Get your bot user token**

Once created, you will have to obtain your **token** called `Bot User OAuth Access Token`. You can find it in `OAuth & Permissions section`. It will have a format like the following:

```
xoxb-xxxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
```

**Define your commands**

For this application it will be necessary to define 4 commands. The first one to **register the credentials** of a user, another one to **update** those credentials, another one to **delete** them and the last one to select and make the type of **clocking** in intratime.

To define a command, go to the `slash commands` section and press the `Create new command` button. You will have to type your new command (for example, `/sign_up` to register a user ). It is important that in the `Request URL` field of all commands you type the following settings:

| Example command | Request URL                                                 |
| --------------- |-------------------------------------------------------------|
| `/sign_up`      | `http://<YOUR_SERVER_IP>:<DIALOG_SERVICE_PORT>/sign_up`     |
| `/update_user`  | `http://<YOUR_SERVER_IP>:<DIALOG_SERVICE_PORT>/update_user` |
| `/delete_user`  | `http://<YOUR_SERVER_IP>:<DIALOG_SERVICE_PORT>/delete_user` |
| `/register`     | `http://<YOUR_SERVER_IP>:<DIALOG_SERVICE_PORT>/register`    |

> **Note:** The default port used for `dialog-service` is *3000*. You can change that port, but it always has to match the port specified for the **interactive component**.

**Set your interactive component**

The interactive component will allow us to use forms and modal windows to receive user data. This component will be activated after typing one of the above mentioned commands.

To activate this component, go to the `Interactive components` section, activate it by selecting `on` and add the URL that will handle your interactive component (dialog-service).

```
http://<YOUR_SERVER_IP>:<DIALOG_SERVICE_PORT>/interactive
```

**Set your bot user**

The bot will allow us to be able to remember when we have to punch in, and to do so, it will be reading all the users' messages and looking for [specific patterns](https://github.com/jmv74211/Intratime-slack-bot/blob/master/src/config/trigger_patterns.json).

To activate it, go to the `bot user` section , set the requested configuration and save the changes.

> **Note**: In this section you will not need to configure any URL, as the *RTM API* will be used.

## Configure your app settings

In order to correctly configure this application, it is necessary to perform the following steps:

**Set your app configuration credentials**

It is necessary to define a series of variables to establish the credentials and configuration of the services. By default, this configuration must be defined through environment variables.

| Variable                           | Description                   |
| ---------------------------------- | -------------------------------
| `SLACK_API_TOKEN`                  | Your bot user token |
| `CIPHER_KEY`                       | Your string key with which the users' password will be encrypted (symmetrical encryption). It must be exactly 16 or 32 characters long. |
| `MONGO_INITDB_ROOT_USERNAME`       | Your mongo admin username |
| `MONGO_INITDB_ROOT_PASSWORD`       | Your mongo admin pasword |
| `ME_CONFIG_BASICAUTH_USERNAME`     | Your username to access mongo-express service |
| `ME_CONFIG_BASICAUTH_PASSWORD `    | Your password to access mongo-express service |
| `ME_CONFIG_MONGODB_ADMINUSERNAME`  | Your mongo admin username for mongo-express |
| `ME_CONFIG_MONGODB_ADMINPASSWORD`  | Your mongo admin password for mongo-express |
| `MONGO_DB_USER`                    | Your mongo admin username for user-service |
| `MONGO_DB_PASSWORD`                | Your mongo admin password for user-service |

You can configure, and copy these variables to your terminal to add them.

```bash
export SLACK_API_TOKEN="<YOUR_VALUE_HERE>"
export CIPHER_KEY="<YOUR_VALUE_HERE>"

export MONGO_DB_USER="<YOUR_VALUE_HERE>"
export MONGO_DB_PASSWORD="<YOUR_VALUE_HERE>"
export MONGO_INITDB_ROOT_USERNAME="<YOUR_VALUE_HERE>"
export MONGO_INITDB_ROOT_PASSWORD="<YOUR_VALUE_HERE>"

export ME_CONFIG_BASICAUTH_USERNAME="<YOUR_VALUE_HERE>"
export ME_CONFIG_BASICAUTH_PASSWORD="<YOUR_VALUE_HERE>"
export ME_CONFIG_MONGODB_ADMINUSERNAME="<YOUR_VALUE_HERE>"
export ME_CONFIG_MONGODB_ADMINPASSWORD="<YOUR_VALUE_HERE>"
```

> **Note**: It is recommended to add this block to the `~/.bashrc` file so that it is automatically added after every system start. After adding them, you will have to reload the configuration of this file from your shell. You can do this with the command: `source ~/.bashrc`

**Set your app configuration**

The application has a configuration file called [settings.py](https://github.com/jmv74211/Intratime-slack-bot/blob/master/src/config/settings.py).

In this file you can specify various general information, such as service ports, names...

It is recommended to leave this configuration by default, since any change in the ports or service names will also have to be made in the deployment file [docker-compose.yaml](https://github.com/jmv74211/Intratime-slack-bot/blob/master/docker-compose.yaml).

**The only mandatory field to be modified** is the `ADMIN_USER` field, in which you will have to enter the `user_id` of the slack application administrator user. The functionality of this is to be able to send private messages to the administrator in case of a service failure.

## Deploy the app

Once the application is configured (see the previous steps), deploying the application is very simple, you just need to have installed [docker](https://www.docker.com/get-started) and  [docker-compose](https://docs.docker.com/compose/install/) and execute the following command in root directory.

```bash
docker-compose build && docker-compose up
```

---

# Contributions

Any doubt or suggestion, you can create issues and/or make pull requests :)