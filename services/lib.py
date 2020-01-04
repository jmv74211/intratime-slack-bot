from Crypto import Random
from Crypto.Cipher import AES
import os

CIPHER_KEY = os.environ['cipher_key'].encode()
ENCODING = 'cp437'

################################################################################################

def encrypt(message, key_size=256):

  pad = b"\0" * (AES.block_size - len(message) % AES.block_size)
  message = message + pad.decode()
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(CIPHER_KEY, AES.MODE_CBC, iv)

  return iv + cipher.encrypt(message)

################################################################################################

def decrypt(ciphertext):

  iv = ciphertext[:AES.block_size]
  cipher = AES.new(CIPHER_KEY, AES.MODE_CBC, iv)
  plaintext = cipher.decrypt(ciphertext[AES.block_size:])

  return plaintext.rstrip(b"\0")