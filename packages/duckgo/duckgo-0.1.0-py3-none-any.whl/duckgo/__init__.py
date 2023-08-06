import re
from typing import Optional, List

import requests

from duckgo.types import ImageResult, WebResult, VideoResult

HEADER_DEFAULT = {
    "User-Agent": "DuckGo/0.1.0 (Python)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Cache-Control": "max-age=0",
}

DUCK_URL = 'https://duckduckgo.com/'
DUCK_LINKS_URL = 'https://links.duckduckgo.com/'

EXTRACT_VQD_PATTERN = re.compile(r'vqd=([\d-]+)&')


def _get_vqd_token(q: str) -> Optional[str]:
    r = requests.get(url=DUCK_URL, params={'q': q}, headers=HEADER_DEFAULT)
    vqd_pattern = EXTRACT_VQD_PATTERN.search(r.text)
    if not vqd_pattern:
        raise RuntimeError('Could not find the `vqd` value in the response from the site.')
    return vqd_pattern.group(1)


def _get_json(url, params: Optional[dict] = None):
    r = requests.get(url, params=params, headers=HEADER_DEFAULT)
    if r.status_code != 200:
        raise RuntimeError('Could not get the results from the site (status: %s).' % r.status_code)
    return r.json()


def web(
        q: str,
        n_results: Optional[int] = None
) -> List[WebResult]:
    vqd_token = _get_vqd_token(q)
    params = dict(o='json', q=q, vqd=vqd_token)
    json_resp = _get_json(DUCK_LINKS_URL + '/d.js', params)

    output = []
    n_results = len(json_resp['results']) if n_results is None else n_results
    while len(output) < n_results:
        resp_results = json_resp['results']
        # The next page url is expected to be in the last result.
        # resp_results = [... {a: "...", ae: ..., }, { n: "/d.js?q=..." }]
        for resp_result in resp_results:
            if 'n' in resp_result:
                next_url = DUCK_LINKS_URL + resp_result['n']
                json_resp = _get_json(next_url)
                break
            output.append(WebResult(resp_result))
            if len(output) >= n_results:
                break
    return output


def image(
        q: str,
        n_results: Optional[int] = None
) -> List[ImageResult]:
    vqd_token = _get_vqd_token(q)
    params = dict(o='json', q=q, vqd=vqd_token)
    json_resp = _get_json(DUCK_URL + '/i.js', params)

    output = []
    n_results = len(json_resp['results']) if n_results is None else n_results
    while len(output) < n_results:
        resp_results = json_resp['results']
        for i in range(len(resp_results)):
            output.append(ImageResult(resp_results[i]))
            if len(output) >= n_results:
                break
        else:
            next_url = DUCK_URL + json_resp['next']
            json_resp = _get_json(next_url, params)
    return output


def video(
        q: str,
        n_results: Optional[int] = None
) -> List[VideoResult]:
    vqd_token = _get_vqd_token(q)
    params = dict(o='json', q=q, vqd=vqd_token)
    json_resp = _get_json(DUCK_URL + '/v.js', params)

    output = []
    n_results = len(json_resp['results']) if n_results is None else n_results
    while len(output) < n_results:
        resp_results = json_resp['results']
        for i in range(len(resp_results)):
            output.append(VideoResult(resp_results[i]))
            if len(output) >= n_results:
                break
        else:
            next_url = DUCK_URL + json_resp['next']
            json_resp = _get_json(next_url, params)
    return output


if __name__ == '__main__':
    results = web('panda', n_results=101)
    for result in results:
        print(result.title, result.url)
