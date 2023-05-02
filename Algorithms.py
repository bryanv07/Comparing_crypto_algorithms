#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2023 AbrahamRH <abrahamrzhz@gmail.com>
#
# Distributed under terms of the MIT license.

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from time import process_time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto import Random
from Crypto.Signature import pss
from Crypto.Hash import SHA256

import rsa
import os
import base64
import hashlib #Used for SHA2 and SHA3 Algorithms 
import binascii
import vectores
#pip install pycryptodome
#pip install rsa


KEY_256 = os.urandom(32)
KEY_512 = os.urandom(64)
NONCE = os.urandom(16)

def RSA_PSS(vectores):
    msg = vectores
    encryption_time_start = process_time()
    key = RSA.import_key(open('privkey.der').read())
    h = SHA256.new(msg)
    signature = pss.new(key).sign(h)
    encryption_time_end = process_time()
    encryption_time = encryption_time_end - encryption_time_start

    decryption_time_start = process_time()
    key = RSA.import_key(open('pubkey.der').read())
    h = SHA256.new(msg)
    verifier = pss.new(key)
    try:
      verifier.verify(h, signature)
      print ("The signature is authentic.")
    except (ValueError, TypeError):
      print ("The signature is not authentic.")
    decryption_time_end = process_time()
    decryption_time = decryption_time_end - decryption_time_start
    return (encryption_time,decryption_time)


def RSA_OAEP(vectores):
    msg = vectores
    #Encryption
    encryption_time_start = process_time()
    key = RSA.generate(2048)
    private_key = key.export_key('PEM')
    public_key = key.publickey().exportKey('PEM')
    msg = str.encode(msg)
    rsa_public_key = RSA.importKey(public_key)
    rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
    cypherText = rsa_public_key.encrypt(msg)
    encryption_time_end = process_time()
    encryption_time = encryption_time_end - encryption_time_start 
    #Decryption
    decryption_time_start = process_time()
    rsa_private_key = RSA.importKey(private_key)
    rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
    decrypted_text = rsa_private_key.decrypt(cypherText)
    decryption_time_end = process_time()
    decryption_time = decryption_time_end - decryption_time_start
    return (encryption_time,decryption_time)

def testSHA3(vectores):
    msg = vectores
    encryption_time_start = process_time()
    msg = bytes(msg, 'utf-8')
    cypherText = hashlib.sha3_512()
    cypherText = cypherText.update(msg)
    encryption_time_end = process_time()
    encryption_time = encryption_time_end - encryption_time_start 
    decryption_time_start = process_time()
    #It is not possible to decrypt a message crphered with SHA3
    cypherText = cypherText.hexdigest()
    decryption_time = 0
    return (encryption_time,decryption_time)

def testSHA2(vectores):
    msg = vectores
    encryption_time_start = process_time()
    cypherText = hashlib.sha512(msg.encode())
    encryption_time_end = process_time()
    encryption_time = encryption_time_end - encryption_time_start 
    decryption_time_start = process_time()
    #It is not possible to decrypt a message crphered with SHA2
    cypherText = cypherText.hexdigest()
    decryption_time = 0
    return (encryption_time,decryption_time)


def testChacha(vectores):
    print("="*23)
    print("--- Prueba ChaCha20 ---")
    print("="*23)
    test_vectors = vectores.generate_test_vectors(6, 100000)
    promedio_encryption = {}
    promedio_decryption = {}
    for i, vector in enumerate(test_vectors):
        print(f"Vector de prueba #{i+1}:")
        encryption_times = []
        decryption_times = []
        for j in range(len(vector["nonces"])):
            key = vector["key"][j]
            plaintext = vector["plaintexts"][j]
            nonce = vector["nonces"][j]
            cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
            encryptor = cipher.encryptor()
            decryptor = cipher.decryptor()

            encryption_time_start = process_time()
            cipherText = encryptor.update(plaintext) + encryptor.finalize()
            encryption_time_end = process_time()
            encryption_time = encryption_time_end - encryption_time_start 
            encryption_times.append(encryption_time)

            decryption_time_start = process_time()
            decryptedText = decryptor.update(cipherText) + decryptor.finalize()
            decryption_time_end = process_time()
            decryption_time = decryption_time_end - decryption_time_start
            decryption_times.append(decryption_time)

        promedio_encryption[i+1] = sum(encryption_times)/len(encryption_times)
        promedio_decryption[i+1] = sum(decryption_times)/len(decryption_times)
        print(f"Tiempo promedio de cifrado del vector de prueba #{i+1}: {promedio_encryption[i+1]:.6f} segundos")
        print(f"Tiempo promedio de descifrado del vector de prueba #{i+1}: {promedio_decryption[i+1]:.6f} segundos")
    return (promedio_encryption,promedio_decryption)
    
def testECB(vectores):
    print("="*23)
    print("--- Prueba AES ECB ---")
    print("="*23)
    test_vectors = vectores.generate_test_vectors(6, 100000)
    promedio_encryption = {}
    promedio_decryption = {}
    for i, vector in enumerate(test_vectors):
        print(f"Vector de prueba #{i+1}:")
        encryption_times = []
        decryption_times = []
        for j in range(len(vector["nonces"])):
            padding_length = 16 - (len(vector["key"][j]) % 16)
            key = vector["key"][j]
            plaintext = vector["plaintexts"][j]
            nonce = vector["nonces"][j]
            cipher = Cipher(algorithms.AES(key), mode=modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()
            decryptor = cipher.decryptor()

            encryption_time_start = process_time()
            cipherText = encryptor.update(plaintext) + encryptor.finalize()
            encryption_time_end = process_time()
            encryption_time = encryption_time_end - encryption_time_start 
            encryption_times.append(encryption_time)


            decryption_time_start = process_time()
            plaintext = decryptor.update(cipherText) + decryptor.finalize()
            decryption_time_end = process_time()
            decryption_time = decryption_time_end - decryption_time_start
            decryption_times.append(decryption_time)

        promedio_encryption[i+1] = sum(encryption_times)/len(encryption_times)
        promedio_decryption[i+1] = sum(decryption_times)/len(decryption_times)
        print(f"Tiempo promedio de cifrado del vector de prueba #{i+1}: {promedio_encryption[i+1]:.6f} segundos")
        print(f"Tiempo promedio de descifrado del vector de prueba #{i+1}: {promedio_decryption[i+1]:.6f} segundos")
    return (promedio_encryption,promedio_decryption)

def testGCM(vectores):
    msg = vectores
    cipher = AES.new(KEY_256, AES.MODE_GCM,NONCE)

    encryption_time_start = process_time()
    cipherText, tag = cipher.encrypt_and_digest(msg)
    encryption_time_end = process_time()
    encryption_time = encryption_time_end - encryption_time_start 

    cipher = AES.new(KEY_256, AES.MODE_GCM,NONCE)
    decryption_time_start = process_time()
    plaintext = cipher.decrypt(cipherText)
    decryption_time_end = process_time()
    decryption_time = decryption_time_end - decryption_time_start
    print(plaintext)
    return (encryption_time,decryption_time)


def getData():
    data_encryption, data_decryption = testChacha(vectores)
    print("")
    data_encryption, data_decryption = testECB(vectores)







if __name__ == "__main__":
    getData()
