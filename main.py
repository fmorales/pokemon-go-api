import argparse
import dirty
from getpass import getpass
import login
import os
import platform


def get_acces_token(usr, pws, type):
    access_token = None
    ltype = None
    if 'goo' in type:
        print '[!] Using google as login..'
        google_data = None
        if platform.system() == 'Windows':
            google_data = login.login_google(usr, pws)
            if google_data is not None:
                access_token = google_data['id_token']
        else:
            access_token = login.login_google_v2(usr, pws)
        if access_token is not None:
            ltype = 'google'
    else:
        print '[!] I am a poketrainer..'
        access_token = login.login_pokemon(usr, pws)
        ltype = 'ptc'
    dirty.accessToken = access_token
    dirty.globalltype = ltype
    return access_token, ltype


def main():
    if platform.system() == 'Windows':
        os.system("title Pokemon GO API Python")
        os.system("cls")
    else:
        # Catches "Lunux" and "Darwin" (OSX), among others
        os.system("clear")
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Login", default=None)
    parser.add_argument("-p", "--password", help="Password", default=None)
    parser.add_argument("-t", "--type", help="Google/PTC", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    dirty.argsStored = parser.parse_args()
    if not dirty.argsStored.username:
        dirty.argsStored.username = getpass("Username: ")
    if not dirty.argsStored.password:
        dirty.argsStored.password = getpass("Password: ")
    if dirty.argsStored.type.lower() in ['ptc', 'goo']:
        access_token, ltype = get_acces_token(dirty.argsStored.username,
                                              dirty.argsStored.password,
                                              dirty.argsStored.type.lower())
        if access_token is not None:
            dirty.start_private_show(access_token, ltype,
                                     dirty.argsStored.location)
        else:
            print '[-] access_token bad'
    else:
        msg = '[!] used type "%s" only Google or PTC valid'
        print msg % (dirty.argsStored.type.lower())

if __name__ == '__main__':
    main()
