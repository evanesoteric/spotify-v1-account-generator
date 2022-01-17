#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
    spotgen
    ~~~~~~~

    Spotify account generator
'''

import subprocess
from time import sleep
from random import randrange
import random
import string
from multiprocessing import Pool, get_context
import requests
from faker import Faker
from db import *


# init
fake = Faker()
email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'hotmail.co.uk', 'hotmail.fr', 'outlook.com', 'icloud.com', 'mail.com', 'live.com', 'yahoo.it', 'yahoo.ca', 'yahoo.in', 'live.se', 'orange.fr', 'msn.com', 'mail.ru', 'mac.com']


# import proxies
def load_proxies():
    with open('proxies.txt', 'r') as f:
        p = f.read().splitlines()
        p = list(filter(None, p))
    return p


# generate credentials/persona
def cred_gen():
    full_name = fake.name().split(' ')
    first_name = full_name[0]
    last_name = full_name[1]
    random_string = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(11))
    email = first_name + random_string[:-4] + '@' + random.choice(email_domains)
    email = email.lower()
    password = random_string
    display_name = first_name
    gender = random.choice(['male', 'female'])
    birth_day = random.randint(1, 28)
    birth_month = random.randint(1, 12)
    birth_year = random.randint(1969, 2001)
    return first_name, last_name, email, password, display_name, gender, birth_day, birth_month, birth_year


# re-indent after testing
def gen_account(proxy):
    # start session
    s = requests.Session()

    # proxify session
    s.proxies = {
        'http': 'socks5h://' + proxy,
        'https': 'socks5h://' + proxy,
        }

    # generate credentials
    first_name, last_name, email, password, display_name, gender, birth_day, birth_month, birth_year = cred_gen()

    # format birth_date strings
    if birth_day < 10:
        birth_day = '0' + str(birth_day)
    else:
        birth_day = str(birth_day)
    if birth_month < 10:
        birth_month = '0' + str(birth_month)
    else:
        birth_month = str(birth_month)
    birth_date = str(birth_year) + '-' + str(birth_month) + '-' + str(birth_day)

    # prepare db insert
    ins = accounts.insert().values(
        first_name = first_name,
        last_name = last_name,
        email = email,
        password = password,
        display_name = display_name,
        gender = gender,
        birth_date = birth_date,
        verified = False,
        password_reset = False,
        in_use = False,
        )

    # post headers
    headers = {
        "User-Agent": "Spotify/8.5.86.739; iOS/13.5.1(iPhone12, 8)",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept": "application/json, text/plain;q=0.2, */*;q=0.1",
        "App-Platform": "IOS",
        "Accept-Language": "en-TZ;q=1.0",
        "Accept-Encoding": "gzip;q=1.0, compress;q=0.5",
        }

    # post data
    data = {
        "displayname": first_name,
        # testing: "creation_point": "https://www.spotify.com/us/signup?utm_source=spotify&utm_medium=desktop-win32&utm_campaign=organic",
        "creation_point": "https://login.app.spotify.com?utm_source=spotify&utm_medium=desktop-win32&utm_campaign=organic",
        "birth_month": birth_month,
        "email": email,
        "password": password,
        "creation_flow": "desktop",
        "platform": "desktop",
        "birth_year": birth_year,
        "iagree": "1",
        "key": "4c7a36d5260abca4af282779720cf631",  # howto generate random accepted key?
        "birth_day": birth_day,
        "gender": gender,
        "password_repeat": password,
        "referrer": ""
        }

    # signup url
    url = "https://spclient.wg.spotify.com/signup/public/v1/account"

    # create account
    try:
        r = s.post(url, headers=headers, data=data, timeout=10).json()
        s.close()

        print(r['status'])

        # proxy service forbidden
        if r['status'] == 320:
            pass

        if r['status'] == 1:
            # account created successfully
            credentials = email + ':' + password
            print(credentials)

            # database inster transaction
            with db.connect() as conn:
                trans = conn.begin()
                try:
                    conn.execute(ins)
                    trans.commit()
                except exc.IntegrityError:
                    # UNIQUE constraint error
                    trans.rollback()
                except Exception as e:
                    print(e)
                    trans.rollback()

            # return proxy for reuse
            return proxy
    except requests.exceptions.Timeout as e:
        # proxy timeout error
        pass
    except Exception as e:
        pass


def main():
    # generate accounts
    with get_context("spawn").Pool(processes=4) as pool:
        new_accounts = list(pool.imap_unordered(gen_account, proxies))

    # remove None types from list
    # new_accounts = list(filter(None, new_accounts))
    # good_proxies = list(filter(None, proxies))

    ## export accounts
    # if len(new_accounts) > 0:
    #     print(str(len(new_accounts)), 'accounts generated.\n')
    #     with open('accounts.txt', 'a+') as f:
    #         for item in new_accounts:
    #             f.write(item + '\n')
    # else:
    #     print('Could not generate any accounts.\n')
    #
    ##

    ## reuse good proxies again
    # cycles = 1
    # while True:
    #     if cycles <= 0:
    #         break
    #     cycles -= 1
    #     # processes set as 4 for safety
    #     with get_context("spawn").Pool(processes=4) as pool:
    #         good_proxies = list(pool.imap_unordered(gen_account, good_proxies))
    #
    #     # sleep random
    #     randsleep = randrange(100, 600)
    #     sleep(randsleep)
    #
    #     # remove duplicate proxies from good_proxies
    #     good_proxies = list(set(good_proxies))
    #     good_proxies = list(filter(None, proxies))
    #
    # remove duplicate proxies from good_proxies
    # good_proxies = list(set(good_proxies))
    # good_proxies = list(filter(None, proxies))
    #
    # export good_proxies to good-proxies.txt
    # if len(good_proxies) > 0:
    #    print(str(len(good_proxies)), 'proxies are working.\n')
    #    with open('good-proxies.txt', 'w+') as f:
    #        for item in good_proxies:
    #            f.write(item + '\n')
    # else:
    #    print('No proxies worked.\n')
    #
    ##


if __name__ == '__main__':
    new_accounts = []
    good_proxies = []
    proxies = load_proxies()  # import proxies as list
    if len(proxies) == 0:
        print('Proxylist is empty. Exiting!')
