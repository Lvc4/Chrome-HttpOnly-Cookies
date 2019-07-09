import sqlite3
import sys
from os import getenv, path
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import keyring

def get_cookies(url, cookiesfile):

    def chrome_decrypt(encrypted_value, key=None):
        dec = AES.new(key, AES.MODE_CBC, IV=iv).decrypt(encrypted_value[3:])
        decrypted = dec[:-dec[-1]].decode('utf8')
        return decrypted

    cookies = []
    if sys.platform == 'win32':
        import win32crypt
        conn = sqlite3.connect(cookiesfile)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, value, encrypted_value FROM cookies WHERE host_key == "' + url + '"')
        for name, value, encrypted_value in cursor.fetchall():
            if value or (encrypted_value[:3] == b'v10'):
                cookies.append((name, value))
            else:
                decrypted_value = win32crypt.CryptUnprotectData(
                    encrypted_value, None, None, None, 0)[1].decode('utf-8') or 'Etwas ist schiefgelaufen'
                cookies.append((name, decrypted_value))

    elif sys.platform == 'linux':
        my_pass = 'peanuts'.encode('utf8')
        iterations = 1
        key = PBKDF2(my_pass, salt, length, iterations)
        conn = sqlite3.connect(cookiesfile)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, value, encrypted_value FROM cookies WHERE host_key == "' + url + '"')
        for name, value, encrypted_value in cursor.fetchall():
            decrypted_tuple = (name, chrome_decrypt(encrypted_value, key=key))
            cookies.append(decrypted_tuple)

    elif sys.platform == 'darwin':
        my_pass = keyring.get_password('Chrome Safe Storage', 'Chrome')
        my_pass = my_pass.encode('utf8')
        iterations = 1
        key = PBKDF2(my_pass, salt, length, iterations)
        conn = sqlite3.connect(os.path.expanduser(cookiesfile))
        cursor = conn.cursor()
        cursor.execute(
            'SELECT name, value, encrypted_value FROM cookies WHERE host_key == "' + url + '"')
        for name, value, encrypted_value in cursor.fetchall():
            decrypted_tuple = (name, chrome_decrypt(encrypted_value, key=key))
            cookies.append(decrypted_tuple)
    else:
        print('Dieses Tool funktioniert nur unter Windows, Linux und OS X')

    conn.close()
    return cookies


if __name__ == '__main__':
    pass
else:
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

#get_cookies('.web.whatsapp..com', cookiesfile)