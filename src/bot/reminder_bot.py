import re
import string
import unidecode
import os
import slack
import json
import sys
import requests
import datetime
sys.path.insert(0, '../config')
sys.path.insert(0, '../lib')
import settings
import utils
import global_messages

PATTERS_FILE = '../config/trigger_patterns.json'

with open(PATTERS_FILE, 'r') as f:
  patterns = json.loads(f.read())

#-------------------------------------------------------------------------------

def pre_process_text(input_text, user_input=False):

    input_text = input_text.lower() # Lowercase
    input_text = re.sub(r'\d+', '', input_text) # Remove numbers
    input_text = re.sub(' +', ' ', input_text) # Remove multiple whitespaces
    input_text = input_text.strip() # Remove initial and end whitespaces
    input_text = unidecode.unidecode(input_text) # Remove acents

    if user_input: # Try to avoid delete regex patterns
      input_text = input_text.translate(str.maketrans('','',string.punctuation)) # Remove puntuaction

    return input_text

#-------------------------------------------------------------------------------

def post_ephemeral_message(web_client, channel_id, block_message, user):

  web_client.chat_postEphemeral(
    channel=channel_id,
    blocks=block_message,
    user=user
  )

#-------------------------------------------------------------------------------

def post_thread_message(web_client, channel_id, text, thread_ts):

  web_client.chat_postMessage(
    channel=channel_id,
    text=text,
    thread_ts=thread_ts
  )

#-------------------------------------------------------------------------------

def generate_reminder_message(user_display_name, action):

  action_text = {
    'IN': global_messages.IN_MESSAGE,
    'PAUSE': global_messages.PAUSE_MESSAGE,
    'RETURN': global_messages.RETURN_MESSAGE,
    'LEAVE': global_messages.LEAVE_MESSAGE
  }

  block_message = \
    [
      {
			"type": "divider"
		  },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "Hola *@{}*\n Te recuerdo que si vas a *{}* tienes que anotarlo en *intratime*! :sunglasses:\
            \n Para ello, puedes utilizar el commando `/register`  :wink:"
            .format(user_display_name ,action_text[action])
        },
        "accessory": {
          "type": "image",
          "image_url": settings.BOT_URL_IMAGE,

          "alt_text": "Intratime logo"
        }
      },
      {
			"type": "divider"
		  }
    ]

  return block_message

#-------------------------------------------------------------------------------

def get_user_display_name(user_id):

  payload = {'token': settings.SLACK_API_TOKEN, 'user': user_id}
  headers = {'content-type': 'application/x-www-form-urlencoded'}

  request = requests.post("https://slack.com/api/users.info", params=payload, headers=headers)

  user_display_name = request.json()['user']['profile']['display_name']
  if user_display_name == '':
    user_display_name = request.json()['user']['profile']['first_name']

  return user_display_name

#-------------------------------------------------------------------------------

def check_patterns(web_client, channel_id, thread_ts, text_data, user_id):

  for item in patterns['in']:
    if re.match(pre_process_text(item), text_data):
      user_display_name = get_user_display_name(user_id)
      block_message = generate_reminder_message(user_display_name, 'IN')
      post_ephemeral_message(web_client, channel_id, block_message, user_id)
      return

  for item in patterns['pause']:
    if re.match(pre_process_text(item), text_data):
      user_display_name = get_user_display_name(user_id)
      block_message = generate_reminder_message(user_display_name, 'PAUSE')
      post_ephemeral_message(web_client, channel_id, block_message, user_id)
      return

  for item in patterns['return']:
    if re.match(pre_process_text(item), text_data):
      user_display_name = get_user_display_name(user_id)
      block_message = generate_reminder_message(user_display_name, 'RETURN')
      post_ephemeral_message(web_client, channel_id, block_message, user_id)
      return

  for item in patterns['leave']:
    if re.match(pre_process_text(item), text_data):
      print("text_data = {}".format(text_data))
      user_display_name = get_user_display_name(user_id)
      block_message = generate_reminder_message(user_display_name, 'LEAVE')
      post_ephemeral_message(web_client, channel_id, block_message, user_id)
      return

#-------------------------------------------------------------------------------

def print_output_log(user, text):

  date_time = datetime.datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")
  print("{} | check_pattern_event | user: {} | text: {}".format(date_time, user, text))

#-------------------------------------------------------------------------------

@slack.RTMClient.run_on(event='message')
def check_pattern_event(**payload):

    data = payload['data']
    web_client = payload['web_client']

    text_data = pre_process_text(data.get('text',''), user_input=True)
    user = data.get('user', None)

    # Thread messages
    if user is None:
      try:
        user = data.get('message', '').get('user','')
      except:
        user = 'anonymous'

    try:
      print_output_log(user, text_data)
      check_patterns(web_client, data['channel'], data['ts'], text_data, user)
    except Exception as e:
      utils.log(settings.BOT_SERVICE_NAME, 'check_pattern_event', 'ERROR', "exception = {} \
       \ndata = {}".format(str(e), data))

#------------------------------------------------------------------------------#
#                                  MAIN                                        #
#------------------------------------------------------------------------------#

print("BOT RUNNING!")
rtm_client = slack.RTMClient(token=settings.SLACK_API_TOKEN)
rtm_client.start()