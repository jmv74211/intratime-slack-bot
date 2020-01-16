from Crypto import Random
from Crypto.Cipher import AES
import os
import sys
import requests
sys.path.insert(0, '../config')
sys.path.insert(0, '../lib')
import settings
import global_vars

CIPHER_KEY = settings.CIPHER_KEY.encode()
ENCODING = 'cp437'

#-------------------------------------------------------------------------------

def encrypt(message, key_size=256):

  pad = b"\0" * (AES.block_size - len(message) % AES.block_size)
  message = message + pad.decode()
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(CIPHER_KEY, AES.MODE_CBC, iv)

  return iv + cipher.encrypt(message)

#-------------------------------------------------------------------------------

def decrypt(ciphertext):

  iv = ciphertext[:AES.block_size]
  cipher = AES.new(CIPHER_KEY, AES.MODE_CBC, iv)
  plaintext = cipher.decrypt(ciphertext[AES.block_size:])

  return plaintext.rstrip(b"\0")

#-------------------------------------------------------------------------------

def log(service, function, log_type, message):

  payload = {'service': service, 'function': function, 'type': log_type, 'message': message}
  headers = {'content-type': 'application/json'}

  request = requests.post("{}/{}".format(global_vars.LOGGER_SERVICE_URL, 'log'),
    json=payload, headers=headers)

  print("request = {}".format(request.text))

  if request.status_code != 200:
    return False

  return True
