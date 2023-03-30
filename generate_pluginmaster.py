import json
import os
from time import time
from sys import argv
from os.path import getmtime

DOWNLOAD_URL = '{repo_url}/releases/latest/download/latest.zip'

DEFAULTS = {
    'IsHide': False,
    'IsTestingExclusive': False,
    'ApplicableVersion': 'any',
}

DUPLICATES = {
    'DownloadLinkInstall': ['DownloadLinkTesting', 'DownloadLinkUpdate'],
}

TRIMMED_KEYS = [
    'Author',
    'Name',
    'Punchline',
    'Description',
    'Changelog',
    'InternalName',
    'AssemblyVersion',
    'RepoUrl',
    'ApplicableVersion',
    'Tags',
    'CategoryTags',
    'DalamudApiLevel',
    'IconUrl',
    'ImageUrls',
]

def main():
    # extract the manifests from the repository
    master = extract_manifests()

    # trim the manifests
    master = [trim_manifest(manifest) for manifest in master]

    # convert the list of manifests into a master list
    add_extra_fields(master)

    # write the master
    write_master(master)

def extract_manifests():
    manifests = []

    for dirpath, dirnames, filenames in os.walk('./plugins'):
        plugin_name = dirpath.split('/')[-1]
        if len(filenames) == 0 or f'{plugin_name}.json' not in filenames:
            continue
        with open(f'{dirpath}/{plugin_name}.json', 'r') as f:
            manifest = json.loads(f.read())
            manifests.append(manifest)

    return manifests

def add_extra_fields(manifests):
    for manifest in manifests:
        # generate the download link from the internal assembly name
        manifest['DownloadLinkInstall'] = DOWNLOAD_URL.format(repo_url=manifest['RepoUrl'])
        # add default values if missing
        for k, v in DEFAULTS.items():
            if k not in manifest:
                manifest[k] = v
        # duplicate keys as specified in DUPLICATES
        for source, keys in DUPLICATES.items():
            for k in keys:
                if k not in manifest:
                    manifest[k] = manifest[source]
        manifest['DownloadCount'] = 0
        manifest['LastUpdate'] = str(int(getmtime(f'./plugins/{manifest['InternalName']}/{manifest['InternalName']}.json')))

def write_master(master):
    # write as pretty json
    with open('pluginmaster.json', 'w') as f:
        json.dump(master, f, indent=4)

def trim_manifest(plugin):
    return {k: plugin[k] for k in TRIMMED_KEYS if k in plugin}

if __name__ == '__main__':
    main()
