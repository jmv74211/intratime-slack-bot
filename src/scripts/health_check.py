import re
import subprocess

"""
  Script to check the status of services
"""

data_preproccesed = []

ERROR_COLOR = '\033[91m'
OKGREEN_COLOR = '\033[92m'
WARNING_COLOR = '\033[93m'

text_status = subprocess.Popen(['docker-compose', 'ps'] ,stdout=subprocess.PIPE,
  stderr=subprocess.PIPE).communicate()[0].decode().split('\n')

# Proprocess text
for item in text_status:
  if 'intratime-slack-bot' in item:
    data_preproccesed.append(re.sub(r'\s\s+', ' ', item.rstrip().replace('intratime-slack-bot', '').
      replace('-', '').replace('mongod','mongo-express')))

services = ['bot','dialog','intratime','logger','mongoexpress', 'mongo','user']
up_service = 'Up'
down_service = 'Exit'

print()

for item in data_preproccesed:
  for idx in range(len(services)):

    if services[idx] in item:
      if up_service in item:
        print("{}{}-service is UP".format(OKGREEN_COLOR, services[idx]))
        break
      elif down_service in item:
        print("{}{}-service is DOWN".format(ERROR_COLOR, services[idx]))
        break
      else:
        print("{}{}-service is ?????".format(WARNING_COLOR, services[idx] ))
        break

print()