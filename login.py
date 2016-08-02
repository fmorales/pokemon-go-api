import config
import json
from collections import OrderedDict
try:
    from gpsoauth import perform_master_login, perform_oauth
except:
    print '[!] only google_login_v1'
import re
import requests


AID = '9774d56d682e549c'
SVC = 'audience:server:client_id:848232511240-7so421jotr2609rmqakceuu1l' + \
      'uuq0ptb.apps.googleusercontent.com'
APP = 'com.nianticlabs.pokemongo'
CSG = '321187995bc7cdc2b5fc91b11a96e2baa8602c62'


def login_pokemon(user, passw):
    print '[!] doing login for:', user
    try:
        head = {'User-Agent': 'niantic'}
        r = config.s.get(config.login_url, headers=head)
        jdata = json.loads(r.content)

        new_url = r.history[0].headers['Location']
        data = OrderedDict([('lt', jdata['lt']),
                            ('execution', jdata['execution']),
                            ('_eventId', 'submit'),
                            ('username', user),
                            ('password', passw)])

        r1 = config.s.post(new_url, data=data, headers=head,
                           allow_redirects=False)
        raw_ticket = r1.headers['Location']
        if 'errors' in r1.content:
            print json.loads(r1.content)['errors'][0].replace('&#039;', '\'')
            return None
        ticket = re.sub('.*ticket=', '', raw_ticket)

        redirect_uri = 'https://www.nianticlabs.com/pokemongo/error'
        client_secret = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgy' + \
                        'WsbTvWHFLm2wNY0JR'
        data1 = OrderedDict([('client_id', 'mobile-app_pokemon-go'),
                             ('redirect_uri', redirect_uri),
                             ('client_secret', client_secret),
                             ('grant_type', 'refresh_token'),
                             ('code', ticket)])

        r2 = config.s.post(config.login_oauth, data=data1)
        access_token = re.sub('.*en=', '', r2.content)
        access_token = re.sub('.com.*', '.com', access_token)
        return access_token
    except requests.exceptions.RequestException as exception:
        print '[-] pokemon attacking the login server ' + str(exception)
        return None


def login_google_v2(email, passw):
    r1 = perform_master_login(email, passw, AID)
    r2 = perform_oauth(email, r1.get('Token', ''), AID, SVC, APP, CSG)
    return r2['Auth']


def login_google(email, passw):
    try:
        user_agent_info = 'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) ' + \
                          'AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile' + \
                          '/12H143'

        first = 'https://accounts.google.com/o/oauth2/auth?client_id=' + \
                '848232511240-73ri3t7plvk96pj4f85uj8otdat2alem.apps.google' + \
                'usercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.' + \
                '0%3Aoob&response_type=code&scope=openid%20email%20https%3' + \
                'A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email'
        second = 'https://accounts.google.com/AccountLoginInfo'
        third = 'https://accounts.google.com/signin/challenge/sl/password'
        last = 'https://accounts.google.com/o/oauth2/token'

        config.s.headers.update({'User-Agent': user_agent_info})
        r = config.s.get(first)

        GALX = re.search('<input type="hidden" name="GALX" value=".*">',
                         r.content)
        gxf = re.search('<input type="hidden" name="gxf" value=".*:.*">',
                        r.content)
        cont = re.search('<input type="hidden" name="continue" value=".*">',
                         r.content)

        GALX = re.sub('.*value="', '', GALX.group(0))
        GALX = re.sub('".*', '', GALX)

        gxf = re.sub('.*value="', '', gxf.group(0))
        gxf = re.sub('".*', '', gxf)

        cont = re.sub('.*value="', '', cont.group(0))
        cont = re.sub('".*', '', cont)

        data1 = {'Page': 'PasswordSeparationSignIn',
                 'GALX': GALX,
                 'gxf': gxf,
                 'continue': cont,
                 'ltmpl': 'embedded',
                 'scc': '1',
                 'sarp': '1',
                 'oauth': '1',
                 'ProfileInformation': '',
                 '_utf8': '?',
                 'bgresponse': 'js_disabled',
                 'Email': email,
                 'signIn': 'Next'}
        r1 = config.s.post(second, data=data1)

        reg_profile = '<input id="profile-information"' + \
                      ' name="ProfileInformation" type="hidden" value=".*">'
        reg_gxf = '<input type="hidden" name="gxf" value=".*:.*">'
        profile = re.search(reg_profile, r1.content)
        gxf = re.search(reg_gxf, r1.content)

        gxf = re.sub('.*value="', '', gxf.group(0))
        gxf = re.sub('".*', '', gxf)

        profile = re.sub('.*value="', '', profile.group(0))
        profile = re.sub('".*', '', profile)

        data2 = {'Page': 'PasswordSeparationSignIn',
                 'GALX': GALX,
                 'gxf': gxf,
                 'continue': cont,
                 'ltmpl': 'embedded',
                 'scc': '1',
                 'sarp': '1',
                 'oauth': '1',
                 'ProfileInformation': profile,
                 '_utf8': '?',
                 'bgresponse': 'js_disabled',
                 'Email': email,
                 'Passwd': passw,
                 'signIn': 'Sign in',
                 'PersistentCookie': 'yes'}
        r2 = config.s.post(third, data=data2)
        location_header = r2.history[len(r2.history)-1].headers['Location']
        fourth = location_header.replace('amp%3B', '').replace('amp;', '')
        r3 = config.s.get(fourth)

        client_id = re.search('client_id=.*&from_login', fourth)
        client_id = re.sub('.*_id=', '', client_id.group(0))
        client_id = re.sub('&from.*', '', client_id)

        reg_wrapper = '<input id="state_wrapper" type="hidden"' + \
                      ' name="state_wrapper" value=".*">'
        state_wrapper = re.search(reg_wrapper, r3.content)
        state_wrapper = re.sub('.*state_wrapper" value="', '',
                               state_wrapper.group(0))
        state_wrapper = re.sub('"><input type="hidden" .*', '',
                               state_wrapper)

        reg_connect = '<form id="connect-approve" action=".*"' + \
                      ' method="POST" style="display: inline;">'
        connect_approve = re.search(reg_connect, r3.content)
        connect_approve = re.sub('.*action="', '', connect_approve.group(0))
        connect_approve = re.sub('" me.*', '', connect_approve)

        data3 = OrderedDict([('bgresponse', 'js_disabled'),
                             ('_utf8', '☃'),
                             ('state_wrapper', state_wrapper),
                             ('submit_access', 'true')])
        r4 = config.s.post(connect_approve.replace('amp;', ''), data=data3)

        reg_code = '<input id="code" type="text" readonly="readonly"' + \
                   ' value=".*" style=".*" onclick=".*;" />'
        code = re.search(reg_code, r4.content)
        code = re.sub('.*value="', '', code.group(0))
        code = re.sub('" style.*', '', code)

        openid_email = 'openid email https://www.googleapis.com/auth/us' + \
                       'erinfo.email'
        data4 = {'client_id': client_id,
                 'client_secret': 'NCjF1TLi2CcY6t5mt0ZveuL7',
                 'code': code,
                 'grant_type': 'authorization_code',
                 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                 'scope': openid_email}
        r5 = config.s.post(last, data=data4)
        return json.loads(r5.content)
    except:
        print '[-] problem in google login..'
        return None
