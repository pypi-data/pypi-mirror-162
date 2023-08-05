def run(user,passw,usser,intor):
    import os
    import requests
    import random
    import time
    from user_agent import generate_user_agent

    R = '\033[1;31m'
    B = '\033[2;36m'
    G = '\033[1;32m'
    P = '\u001b[35m'
    Y = '\033[1;33m'
    W = "\033[0m"
    print(f'     {G}            Follow4Follow Trail Script\n                    {P}Tele @NamasteHacker\n')
    url = "https://www.instagram.com/accounts/login/ajax/"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "271",
        "content-type": "application/x-www-form-urlencoded",
        'cookie': 'ig_did=34405607-933D-4117-AB09-6DD88E9CC2F7; ig_nrcb=1; mid=YqrOzQABAAHgQxHT9cU-Hy_5kKAO; dpr=3; datr=2_eqYoksU7iaxHB-hJ5metiR; csrftoken=8UiKCpjmrKuFsGz1FRtoIVrTBOj0VCKh',
        "origin": "https://www.instagram.com",
        'referer': 'https://www.instagram.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; RMX2117) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.48 Mobile Safari/537.36',
        'viewport-width': '360',
        'x-asbd-id': '198387',
        'x-csrftoken': '8UiKCpjmrKuFsGz1FRtoIVrTBOj0VCKh',
        'x-ig-app-id': '1217981644879628',
        'x-ig-www-claim': 'hmac.AR1lFVsHGZeq1W-0kNXZMAjWgdDUsZrElLKDkKDvHk1WZ15t',
        'x-instagram-ajax': '1005711565',
    }
    data = {
        "username": user,
        "enc_password": '#PWD_INSTAGRAM_BROWSER:0:&:' + passw
    }
    reqq = requests.post(url, data=data, headers=headers)
    reqcookies = reqq.cookies
    reqtext = reqq.text
    if 'sessionid' in reqcookies:
        print(G + '\nLogged In @' + user + '\n')
        sessionid = reqcookies['sessionid']
        csrftoken = reqcookies['csrftoken']
        ds_user_id = reqcookies['ds_user_id']
    else:
        print(R + 'Wrong Account')
        exit()
    intor = int(intor)
    cookies = {
        'mid': 'YujhJwABAAGPeXYR8GVOQWtpyI6f',
        'ig_did': '67EFAD1D-6E21-42D9-B8C6-5643D4685421',
        'ig_nrcb': '1',
        'csrftoken': str(csrftoken),
        'ds_user_id': str(ds_user_id),
        'sessionid': str(sessionid),
        'shbid': '"19028\\05450549400865\\0541690965184:01f75d661fd13cecd8cf38c8c2289ce3435495a424d66285e3b98aa281babe42e9e2cb4b"',
        'shbts': '"1659429184\\05450549400865\\0541690965184:01f7519d36c03da69cc536635e5cd9491ad7551b41a147c050e82c35991b9815c5a68ab0"',
        'dpr': '3',
        'datr': 'POjoYoyj_QJWbkEC5bq2yHNA',
        'rur': '"EAG\\05450549400865\\0541690967016:01f7ccd6598a5bebc761cb6c9fe765f078bf7cec9c067cf5e8b013ae5656bec64907553a"',
    }
    headers = {
        'authority': 'www.instagram.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # 'content-length': '0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/myfitnesshub/',
        'user-agent': generate_user_agent(),
        'viewport-width': '360',
        'x-asbd-id': '198387',
        'x-csrftoken': 'sW5zeokNi8wAUPXhQ4pdcFEho1BAEP8L',
        'x-ig-app-id': '1217981644879628',
        'x-ig-www-claim': 'hmac.AR1lFVsHGZeq1W-0kNXZNAjWgdDUsZrElLKDrKDvHk1WZ52o',
        'x-instagram-ajax': '1005951515',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {
        'username': usser,
    }
    roe = requests.get('https://i.instagram.com/api/v1/users/web_profile_info/', params=params, cookies=cookies,
                       headers=headers).json()
    ownid = roe['data']['user']['id']
    print(f'{Y}Your Userid => {G}{ownid}')
    while True:
        try:
            print('')
            time.sleep(intor)
            headers0 = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': generate_user_agent(),
            }
            rese = requests.get('https://apievilxnamastexgamer.herokuapp.com/getlist', headers=headers0).text
            # print(rese)
            if '""' in rese:
                print(R + 'Order Not Available ')
            elif '<html>' in rese:
                print(R + 'Order Not Available ')
            elif '"39:26:"' in rese:
                re = requests.get(f'https://apievilxnamastexgamer.herokuapp.com/user/{ownid}').text
                print(R + 'Order Not Available ')
            else:
                # print(rese)
                # print('Order Founded ')
                useris = rese.split(':"')[0]
                userido = useris.split(':')[2]
                # print(userido)
                if '"' in userido:
                    print(R + 'Order Not Available')
                elif int(userido) == int(ownid):
                    print(Y + 'Your Order Running ')
                else:
                    print(Y + 'Victim ID => ' + P + userido)
                    cookies00 = {
                        'mid': 'YujhJwABAAGPeXYR8GVOQWtpyI6f',
                        'ig_did': '67EFAD1D-6E21-42D9-B8C6-5643D4685421',
                        'ig_nrcb': '1',
                        'csrftoken': 'sW5zeokNi8wAUPXhQ4pdcFEho1BAEP8L',
                        'ds_user_id': '50549400865',
                        'sessionid': str(sessionid),
                        'shbid': '"19028\\05450549400865\\0541690965184:01f75d661fd13cecd8cf38c8c2289ce3435495a424d66285e3b98aa281babe42e9e2cb4b"',
                        'shbts': '"1659429184\\05450549400865\\0541690965184:01f7519d36c03da69cc536635e5cd9491ad7551b41a147c050e82c35991b9815c5a68ab0"',
                        'dpr': '3',
                        'datr': 'POjoYoyj_QJWbkEC5bq2yHNA',
                        'rur': '"RVA\\05450549400865\\0541690975916:01f70256a38ea56aacddaa7d8470cd7ebefea92637934262d64b9d2bd9840b493016d04e"',
                    }
                    user00 = '1234567890'
                    us1 = str("".join(random.choice(user00) for i in range(int(1))))
                    us2 = str("".join(random.choice(user00) for i in range(int(1))))
                    us3 = str("".join(random.choice(user00) for i in range(int(1))))
                    us7 = str("".join(random.choice(user00) for i in range(int(1))))
                    user000 = 'QWERTYUIOPASDFGHJKLZXCVBNM'
                    us4 = str("".join(random.choice(user000) for i in range(int(1))))
                    us5 = str("".join(random.choice(user000) for i in range(int(1))))
                    us6 = str("".join(random.choice(user000) for i in range(int(1))))
                    us8 = str("".join(random.choice(user000) for i in range(int(1))))
                    headers00 = {
                        'authority': 'www.instagram.com',
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        # 'content-length': '0',
                        'content-type': 'application/x-www-form-urlencoded',
                        'origin': 'https://www.instagram.com',
                        'referer': 'https://www.instagram.com/theabhinavbhardwaj/',
                        'sec-ch-prefers-color-scheme': 'light',
                        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Linux"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/' + us1 + '.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/9' + us2 + '.0.4951.48 Safari/537.36',
                        'viewport-width': '980',
                        'x-asbd-id': '198387',
                        'x-csrftoken': 'sW5zeokNi8wAUPXhQ4pdcFEho1BAEP8L',
                        'x-ig-app-id': '936619743392459',
                        'x-ig-www-claim': 'hmac.AR' + us1 + '6Npv6s_DnDvV6' + us4 + 'sgNRbF' + us3 + 'i' + us5 + 'O1TZ' + us7 + 'g' + us6 + 'b' + us6 + 'epu6_' + us8 + 'ZYLy' + us2 + '61',
                        'x-instagram-ajax': '1005951653',
                        'x-requested-with': 'XMLHttpRequest',
                    }
                    rlse = requests.post(f'https://www.instagram.com/web/friendships/{userido}/follow/',
                                         cookies=cookies00,
                                         headers=headers00).text
                    if 'ok' in rlse:
                        time.sleep(5)
                        headers1 = {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Cache-Control': 'max-age=0',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': generate_user_agent(),
                        }
                        resko = requests.get(f'https://apievilxnamastexgamer.herokuapp.com/user/{ownid}',
                                             headers=headers1).text
                        if 'success' in resko:
                            print(G + 'Following Done ')
                            print(P + 'Order Added ')
                        else:
                            print(R + 'SerVer OverLoad')
                    else:
                        print(R + 'SomeThing Error')
                    time.sleep(10)
        except:
            print(R + f'Error {P}> {G}Contact @NamasteHackers')
            time.sleep(3)
