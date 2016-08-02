import config
import pokemon_pb2
import time
import requests

local_ses = None
tmp_api = None


def use_api(target_api, prot1):
    try:
        if config.debug:
            print '[!] using api:', target_api
        r = config.s.post(target_api, data=prot1, verify=False)
        return r.content
    except:
        print '[!] repeat use_api'
        time.sleep(3)
        return use_api(target_api, prot1)


def get_rpc_server(access_token, first_data):
    try:
        r = config.s.post(config.api_url, data=first_data, verify=False,
                          timeout=3)
        get_session_data = pokemon_pb2.get_session_data()
        get_session_data.ParseFromString(r.content)
        if get_session_data and get_session_data.rpc_server:
            if 'plfe' in get_session_data.rpc_server:
                return get_session_data
            else:
                get_rpc_server(access_token, first_data)
        else:
            get_rpc_server(access_token, first_data)
    except requests.exceptions.RequestException:
        print '[-] offline..'
        time.sleep(3)
        return get_rpc_server(access_token, first_data)


def get_session(login_data):
    try:
        get_session_data = pokemon_pb2.get_session_data()
        get_session_data.ParseFromString(login_data)
        return get_session_data.ses
    except:
        print '[-] problem get_session'
        return None
