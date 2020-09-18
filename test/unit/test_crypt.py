import pytest

from intratime_slack_bot.lib import crypt

# ----------------------------------------------------------------------------------------------------------------------


TEST_PASSWORD = 'a1b2c3d4e5f6g7h8'
TEST_TEXT = 'hello world'


# ----------------------------------------------------------------------------------------------------------------------


def test_generate_cipher_key():
    assert crypt.generate_cipher_key(TEST_PASSWORD).decode() == 'ZIvR0C4xlGfpnoP-_y7ptRiNvY5hawWm4iMLELF-IDw='

# ----------------------------------------------------------------------------------------------------------------------


def test_encrypt_decrypt():
    ciphered_text = crypt.encrypt(TEST_TEXT, TEST_PASSWORD)
    assert crypt.decrypt(ciphered_text, TEST_PASSWORD) == TEST_TEXT
