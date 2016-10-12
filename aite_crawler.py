#!/usr/bin/env python

import requests
import os
import json
import re
from lxml import etree, html
from requests.adapters import HTTPAdapter

__author__ = 'Toan Nguyen'
__version__ = '1.0.0'

title = """
                 ___  ___  __   __   __        __    __   __        
 /\  |    |    |  |  |__  |__) /  \ /  \ |__/ /__`  /  ` /  \  |\/| 
/~~\ |___ |___ |  |  |___ |__) \__/ \__/ |  \ .__/ .\__, \__/  |  | 
                                                                    
      ___  __      __   __   __        __   ___  __                 
|  | |__  |__)    /__` /  ` |__)  /\  |__) |__  |__)                
|/\| |___ |__)    .__/ \__, |  \ /~~\ |    |___ |  \                
                                                                    
                      By : Toan Nguyen
          me @ nntoan.com
          Version : 1.0.0
A tool to download all ebook's available on
www.allitebooks.com and save them in current
directory.
"""

aite_sm = 'http://www.allitebooks.com/post-sitemap{0}.xml'

urls = []

print(title)

with open('list-of-post-urls-allitbooks.md', 'w') as fp:
    for i in range(1, 8):
        fp.write('\n\n## Post Sitemap {0}\n\n'.format(i))
        req = requests.get(aite_sm.format(i))
        root = etree.fromstring(req.content)
        for sitemap in root:
            url = sitemap.getchildren()[0].text
            fp.write('[{0}]({1})\n'.format(url, url))
            urls.append(url)
        print('Post Sitemap ' + str(i) + ' is done')

down_dict = {}

if not os.path.exists('all-it-ebooks'):
    os.mkdir('all-it-ebooks')

save_dir = os.path.abspath(os.path.join(os.curdir, 'all-it-ebooks'))

print('Crawling in Progress ......\n')
for i, url in enumerate(urls[1:]):
    page = requests.Session()
    page.mount(url, HTTPAdapter(max_retries=5))
    page = page.get(url)
    tree = html.fromstring(page.content)    
    down_link = tree.xpath("//*[@class=\"download-links\"]/a/@href")
    file_name = down_link[0].split('/')[-1]
    title = re.sub('[^A-Za-z0-9]+', '-', file_name.split('.')[0])        
    down_dict[title] = down_link[0]    
    save_loc = os.path.join(save_dir, file_name)

    #Starting to download the files
    data = requests.get(down_link[0], stream=True)
    if not os.path.exists(save_loc):
        print('\nNow writing {0} - {1}'.format(i + 1, file_name))
        with open(save_loc, 'wb') as f:
            print(url)            
            for chunk in data.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
    else:
        print('\nFile Exists. Skipped {0} - {1}'.format(i + 1, file_name))

print('\nAll Urls have been crawled and saved.')
print('\nWriting links to JSON file.\n')

with open('all-it-ebooks-download-links.json', 'w') as fp:
    json.dump(down_dict, fp, indent=4)
    print('\t----- Writing Complete')
