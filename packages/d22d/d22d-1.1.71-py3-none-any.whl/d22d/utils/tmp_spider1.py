import random
import requests
import pyquery
import logging
import os
import wrapt
import traceback
import functools

logger_error = functools.partial(print, '[ERROR]')

TMP_PATH_HTML = 'tmp_html'


def cache_file_html(use_cache_key=None):
    if use_cache_key and not os.path.exists(TMP_PATH_HTML):
        os.makedirs(TMP_PATH_HTML)

    @wrapt.decorator
    def wrapper(func, _instance, args, kwargs):
        cache_path = os.path.join(TMP_PATH_HTML, func.__name__)
        if isinstance(use_cache_key, str) and kwargs.get(use_cache_key) and os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                result = f.read()
        else:
            result = func(*args, **kwargs)
            if result:
                with open(cache_path, 'wb') as f:
                    f.write(result)

        return result

    return wrapper


def catch_ex(exs=None, if_ex_return=None):
    if not exs:
        exs = {
            requests.exceptions.ConnectionError: '[ConnectionError] 代理失效或URL失效',
            requests.exceptions.ConnectTimeout: '[ConnectTimeout] 连接握手超时',
            requests.exceptions.ReadTimeout: '[ReadTimeout] 读取数据过程中超时',
        }

    @wrapt.decorator
    def wrapper(func, _instance, args, kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as ex:
            if type(ex) in exs:
                logger_error('{} {}'.format(exs[type(ex)], func.__name__))
            else:
                logger_error("[{}] {} {}\n{}".format(type(ex), ex, func.__name__, traceback.format_exc()))
            return if_ex_return

    return wrapper


def get_proxies():
    proxies_host = '127.0.0.1'
    proxies_port = 838
    proxies = {
        "http": f"socks5://{proxies_host}:{proxies_port}",
        "https": f"socks5://{proxies_host}:{proxies_port}",
    }
    return proxies


def get_ua():
    return random.choice([
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"])


@catch_ex(if_ex_return='')
@cache_file_html(use_cache_key='_use_cache')
def get_html_www_foxnews_com__us(url=r"https://www.foxnews.com/us", _use_cache=True):
    headers = {"User-Agent": get_ua(), "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "accept-language": "zh-CN,zh;q=0.9", "cache-control": "max-age=0", "if-none-match": "\"25bb8-BFQ7ZWOMfKU4YDyEgU6h4Wn2mUY\"", "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"", "sec-ch-ua-mobile": "?0", "sec-fetch-user": "?1", "upgrade-insecure-requests": "1", "cookie": "usprivacy=1---; _cb_ls=1; AMCVS_17FC406C5357BA6E0A490D4D%40AdobeOrg=1; _gcl_au=1.1.2134648958.1646046277; s_ecid=MCMID%7C41638637718077453753528032271087284514; s_cc=true; _cb=CWD_A7Caz7PyBcFYsY; seerid=12c7906c-d8bb-4e61-a46e-d9d3308736aa; _pbjs_userid_consent_data=3524755945110770; __gads=ID=15c8e93a9891f5be:T=1646046396:S=ALNI_Mb-gDS9vA5T8xnjTQNFsCzzFPtk0Q; _lr_env_src_ats=false; __leap_props=%7B%22lastKnownId%22%3A%22%22%2C%22lastAnonymousProfileId%22%3A%22a342f2b4-dc45-44f2-8d15-8c320400026d%22%2C%22persistAnonId%22%3A%22%22%7D; ajs_anonymous_id=%2287551ccb-c824-4edb-81b6-94ec5d787c3f%22; UID_STATE=false; _csrf=XcW3_klMG6dwUhB42EenlOK1; AKA_A2=A; FXN_flk=1; EID=null; AMCV_17FC406C5357BA6E0A490D4D%40AdobeOrg=2121618341%7CMCIDTS%7C19054%7CMCMID%7C41638637718077453753528032271087284514%7CMCAAMLH-1646651076%7C9%7CMCAAMB-1646821209%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1646223609s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-19059; s_sq=%5B%5BB%5D%5D; seerses=e; _lr_geo_location=GB; _cb_svref=null; _gid=GA1.2.1248839275.1646216977; _clck=gfmme5|1|ezf|0; _lr_retry_request=true; _lr_sampling_rate=100; __qca=I0-1079092977-1646217054016; _uetsid=a86585909a1311ec92775ff1d8ca5d0f; _uetvid=3d5b2700988611ecbdd10f8898cfe481; cto_bundle=Mnrok19iUFdTeE1VNmtielg2JTJGZnVvcVlVbXZtYVN0ZnFxNEhWeDFyb3o1ZDFZWkZQMFQyaXdtZXJRUHpEWmYyWFlPJTJGSHVUQ3VlOWY5cUVsSUlkdlozNlYwSDhYSklucU9Ga2lTSzl4bzRzT1JDS0RJNG8lMkZ5JTJGZkhrN0hTdlVUdlFjVXNrRmtJS3pnREdWc1N3U2tvaCUyRkNwSFB3JTNEJTNE; s_pers=%20s_ppn%3Dfnc%253Aroot%253Aroot%253Achannel%7C1646218229076%3B%20omtr_lv%3D1646218594641%7C1740826594641%3B%20omtr_lv_s%3DLess%2520than%25207%2520days%7C1646220394641%3B%20s_nr%3D1646218594653-Repeat%7C1648810594653%3B; _chartbeat2=.1646046309472.1646218595357.111.Bl0_9wezlNkBMxGf8ChM_h9By9GKj.5; _dc_gtm_UA-128752877-9=1; _ga_NW9WX3ZPEG=GS1.1.1646216976.2.1.1646218595.60; _ga=GA1.1.1883859430.1646046396; _clsk=19i0hp1|1646218597462|6|0|b.clarity.ms/collect; FCNEC=[[\"AKsRol_-qgiB4OjyFkgZjUoOoWHvGBVxL_Ct4ANXpQo6WyOak3A7CZ484t4UraxaHG-T8n9LuyJotJoO5f2EDnci79LixxX3cGf1dn1OWcTSq_GNf-OvQuqU2OOLKhe1v2J-8kDhjQDWVclA1PnCWqG4MFi8Y1vS4w==\"],null,[]]; s_sess=%20omtr_evar17%3Dhp1navus%3B%20s_ppvl%3Dfnc%25253Aus%25253Afront%25253Achannel%252C15%252C25%252C2151%252C1896%252C1197%252C3840%252C2160%252C1%252CL%3B%20SC_LINKS%3D%3B%20s_ppv%3Dus%252C25%252C25%252C2045%252C1896%252C1197%252C3840%252C2160%252C1%252CPL%3B; RT=\"z=1&dm=foxnews.com&si=3797eab4-4e51-46cf-8fcd-2fded16877ec&ss=l09eqs3j&sl=9&tt=107o&bcn=%2F%2F684d0d44.akstat.io%2F&obo=1&ld=1b13x&ul=1bbay\"", "Host": "www.foxnews.com", "Referer": "https://www.foxnews.com/us", "Origin": "https://www.foxnews.com/us", "Connection": "keep-alive", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin"}

    res = requests.get(
        url=url,
        headers=headers,
        verify=False,
        # stream=True,
        stream=False,
        proxies=get_proxies(),
        timeout=125,
    )
    result = res.content
    return result


def task(url):
    pq_html = pyquery.PyQuery(get_html_www_foxnews_com__us(url=url, _use_cache=False) or '<></>')('html')
    for item in pq_html:
        print(item.text)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    task(r"https://www.foxnews.com/us")
