import codefast as cf
from authc.myredis import rc


def shorten_url(uri: str, printout: bool = True) -> str:
    if not uri.startswith('http'):
        uri = f'http://{uri}'

    query_params = {
        'access_token': rc.cn.get('bitly_token').decode(),
        'longUrl': uri
    }
    endpoint = 'https://api-ssl.bitly.com/v3/shorten'
    response = cf.net.get(endpoint, params=query_params)

    data = response.json()
    if printout:
        print(query_params)
        print("{:<20} {}".format("long url", uri))
        print("{:<20} {}".format("shorten url", data['data']['url']))
    return data['data']['url']
