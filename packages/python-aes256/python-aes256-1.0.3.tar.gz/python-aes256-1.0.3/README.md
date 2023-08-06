# ENCRYPT DECRYPT AES 256bit
----------------------------

Install to your environment :
    > pip install python-aes256

How to use :
------------
    Test using python shell :
    > python manage.py shell
    > from pyaes256 import PyAES256
    > a = PyAES256()
    > password = 'g_7me8rl2m#a_h2oresgt2#ni=3_4*!ai*=rtsq)yi!g7_5-51'     

    Encryption Process :
    > enc = a.encrypt('Secret Text',password)
    > print('Encrypt: ', enc)
        Encrypt: {'url': 'REhHcFNaN0tPSzVqNm50UUJ0T2g5dz09', 'salt': b'k4/Ai7zJKUssvup2c+2+3w==', 'iv': b'34YtC6XqlQjo8UfWc4yNcA=='}

    Decryption Process :
    > dec = a.decrypt(url='REhHcFNaN0tPSzVqNm50UUJ0T2g5dz09', salt=b'k4/Ai7zJKUssvup2c+2+3w==', iv=b'34YtC6XqlQjo8UfWc4yNcA==', password=password)
    > print('Decrypt: ', dec)
        Decrypt: b'Secret Text'
    > origin = bytes.decode(dec)
    > print('Origin: ', origin)
        Origin: 'Secret Text'


# Avalanche Effect :
--------------------

How to use :
------------
    Test using python shell :
    > python manage.py shell
    > from pyavalanche import PyAvalanche
    
    > chipper1 = 'Nk9iL05BQmM5bnRES3drVGc0NHZRdz09'
    > chipper2 = 'Z3VFbi9lWDJtS1B5UzE4TGVsMzRHQT09'
    > print('Chipper 1 = ', chipper1)
    > print('Chipper 2 = ', chipper2)
    > ava = PyAvalanche()
    > result = ava.avalanche_effect(chipper1, chipper2)

    Print result :
    > print(result,'%')
        50.0 %
    > print("If more than 50% output bits have changed then the algo have good avalanche effect.")

    