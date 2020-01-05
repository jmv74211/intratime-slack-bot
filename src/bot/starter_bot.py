import re
import string
import unidecode
import os
import slack

""" import os
import slack

client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

response = client.chat_postMessage(
    channel='UPE8LJ72S',
    text="Hello world!")
assert response["ok"]
assert response["message"]["text"] == "Hello world!"
 """


patterns = {
  'in': [
    'Buenos dias',
    'Hola, buenos días',
    'gm',
    'morning'
  ],
  'pause': [
    'salgo a comer',
    'ahora vuelvo',
    'voy a comer'
  ],
  'return': [
    'ya estoy',
    'he vuelto'
  ],
  'leave': [
   'hasta mañana',
   'nos vemos'
  ]
}


def pre_process_text(input_text):

    input_text = input_text.lower() # Lowercase
    input_text = re.sub(r'\d+', '', input_text) # Remove numbers
    input_text = input_text.translate(str.maketrans('','',string.punctuation)) # Remove puntuaction
    input_text = re.sub(' +', ' ', input_text) # Remove multiple whitespaces
    input_text = input_text.strip() # Remove initial and end whitespaces
    input_text = unidecode.unidecode(input_text) # Remove acents

    return input_text

def post_thread_message(web_client, channel_id, text, thread_ts):
  web_client.chat_postMessage(
    channel=channel_id,
    text=text,
    thread_ts=thread_ts
  )

def check_patterns(web_client, channel_id, thread_ts, text_data):

  for item in patterns['in']:
      if pre_process_text(item) in text_data:
        post_thread_message(web_client, channel_id, "IN", thread_ts)

  for item in patterns['pause']:
    if pre_process_text(item) in text_data:
      post_thread_message(web_client, channel_id, "PAUSE", thread_ts)

  for item in patterns['return']:
    if pre_process_text(item) in text_data:
      post_thread_message(web_client, channel_id, "RETURN", thread_ts)

  for item in patterns['leave']:
    if pre_process_text(item) in text_data:
      post_thread_message(web_client, channel_id, "LEAVE", thread_ts)

@slack.RTMClient.run_on(event='message')
def check_pattern_event(**payload):
    data = payload['data']
    web_client = payload['web_client']

    text_data = pre_process_text(data.get('text',''))
    channel_id = data['channel']
    thread_ts = data['ts']

    check_patterns(web_client, channel_id, thread_ts, text_data)

slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
rtm_client.start()