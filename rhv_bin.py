# Docs https://docs.github.com/en/rest/reference/repos#releases

import urllib.request
import urllib.error
import json
import sys
import operator

OSES = {
    ('ubuntu-20.04', 'ubuntu', 'linux'): 'linux',
    ('windows-2019', 'windows', 'win'): 'win'
}
ARCH = {
    ('x32', 'x86', '32', '86', 'i686'): {
        'win': '32',
        'linux': '_i686'
    },
    ('x64', 'x86_64', '64', 'amd64'): {
        'win': '_amd64',
        'linux': '_x86_64'
    },
    ('aarch64', 'arm64', 'arm64v8'): {
        'linux': '_aarch64'
    },
    ('armv7l', 'armv7', 'arm32', 'arm32v7'): {
        'linux': '_armv7l'
    },
}
ENDPOINTS = {
    'bin': 'https://api.github.com/repos/Aculeasis/rhvoice-wrapper-bin/releases',
    'data': 'https://api.github.com/repos/malyushkin/digitil-rhvoice-wrapper-data/releases'
}


def get_release_dict(endpoint: str):
    response = urllib.request.urlopen(
        urllib.request.Request(url=endpoint, headers={'Accept': 'application/vnd.github.v3+json'})
    )
    if response.getcode() != 200:
        raise RuntimeError('Request code error: {}'.format(response.getcode()))
    return json.loads(response.read().decode('utf-8'))


def prepare_release(endpoint: str):
    result = dict()
    for release in get_release_dict(endpoint):
        tag_name = release.get('tag_name')
        if tag_name:
            result[tag_name] = [x.get('browser_download_url', '') for x in release.get('assets', [])]
    return sorted(result.items(), key=operator.itemgetter(0), reverse=True)


def get_argv():
    targets = ['linux', 'x86_64', 'bin']
    return [(sys.argv[i+1] if len(sys.argv) >= i+2 else x).lower() for i, x in enumerate(targets)]


def prepare_data():
    os, arch, target = get_argv()
    endpoint = ENDPOINTS[target]
    if target == 'data':
        return '.whl', endpoint

    for k, v in OSES.items():
        if os in k:
            os = v
            break
    else:
        raise RuntimeError('Wrong OS: {}'.format(os))
    for k, v in ARCH.items():
        if arch in k:
            arch = v[os]
            break
    else:
        raise RuntimeError('Wrong arch: {}'.format(arch))
    return '-py3-none-{os}{arch}.whl'.format(os=os, arch=arch), endpoint


def get_url():
    tail, endpoint = prepare_data()
    for _, targets in prepare_release(endpoint):
        for target in targets:
            if target.endswith(tail):
                return target
    raise RuntimeError('Package not found')


if __name__ == '__main__':
    print(get_url())