import requests


def get_quota():
    """check random.org quota for getting random data"""
    website = "http://www.random.org/quota/"
    params = {
        "format": "plain"
    }
    resp = requests.get(website, params)
    quota = int(resp.text)
    return quota


def get_web_randints(min, max, k=1):
    """get <k> random integer(s) from random.org, default k = 1"""
    website = "http://www.random.org/integers/"
    params = {
        "num": k,
        "min": min,
        "max": max,
        "col": 1,
        "base": 10,
        "format": "plain",
        "rnd": "new"
    }
    got_web_randints = False
    resp = requests.get(website, params)
    while not resp.ok:
        assert get_quota() > 1, "Quota has already run out."
        time.sleep(5)
        resp = requests.get(website, params)
    time_stamp = resp.headers["date"]
    if k == 1:
        result = int(resp.text)
    else:
        web_rand_data = resp.text.split()
        result = list(map(int, web_rand_data))
    return result, time_stamp
