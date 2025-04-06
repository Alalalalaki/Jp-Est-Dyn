"""
This scrpit is to download MC archieve data from official website.
Note: for file code see: https://www.meti.go.jp/statistics/tyo/kougyo/archives/zipfile.html
"""

import os
import shutil
import pandas as pd
import zipfile
from requests_html import HTMLSession
import re
import z2h

input_path = "../Input/Manufacturing_Census/"


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def get_data_links(session):
    url = "https://www.meti.go.jp/statistics/tyo/kougyo/archives/index.html"
    r = session.get(url)
    links = r.html.absolute_links
    links = [l for l in links if '.zip' in l]
    return links


def download_unzip_data(session, links, code='SAN', path=input_path, years=None):
    path = path + code + '/'
    mkdir(path)

    links = sorted([l for l in links if code in l])
    if years:
        links = [l for l in links if l in years]
    names = [path + re.findall('zip/(.+zip)', l)[0] for l in links]

    for l, n in zip(links, names):
        r = session.get(l)
        with open(n, 'wb') as f:
            f.write(r.content)
        year = n[-8:-4]
        if year in ['2003', '2004']:
            path_y = path + f'SAN_{year}'
        else:
            path_y = path
        with zipfile.ZipFile(n, 'r') as zf:
            for file in zf.infolist():
                try:
                    file.filename = z2h.str_z2h(file.filename.encode('cp437').decode('cp932'))
                except:
                    file.filename = z2h.str_z2h(file.filename.encode('cp437').decode('utf-8'))
                zf.extract(file, path=path_y)
        os.remove(n)
        print(f'Download+Unzip: {n}')


def clean_folders(code='SAN', path=input_path):
    path = path + code + '/'
    if code == 'SAN':
        # deal with 1985
        os.rename(path+'SAN_1985/産業編1985', path+'産業編1985')
        shutil.rmtree(path+'SAN_1985')


def main():
    mkdir(input_path)
    session = HTMLSession()
    links = get_data_links(session)
    download_unzip_data(session, links)
    clean_folders()


if __name__ == "__main__":
    main()
