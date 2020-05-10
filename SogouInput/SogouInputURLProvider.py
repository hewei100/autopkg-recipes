#!/usr/bin/env python
import re
import requests
from lxml import html

from autopkglib import Processor, ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["SogouInputURLProvider"]

class SogouInputURLProvider(URLGetter):
    description = "Provides URL to the requested version of SogouInput product."
    input_variables = {
        "product_name": {
            "required": True,
            "description":
                "Product to fetch URL for. One of 'pinyin', 'wubi' or 'editor'.",
        },
        "version": {
            "required": False,
            "description": ("Only for pinyin: Preferred version to download. Examples: '57a'"),
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the requested version of Sogou product.",
        },
    }

    __doc__ = description

    def main(self):
        product_name = self.env["product_name"].lower()
        if product_name == 'editor':
            product_name = 'skineditor'

        if product_name == 'pinyin':
            version = self.env.get('version', '')
            if version and version != 'latest':
                # no way to download a specific older version
                # mac_57a, mac_58a ...
                # url = re.sub(r'(?<=mac_)\d+[a-z]?', version, url)
                product_name = 'mac'
                # http://cdn2.ime.sogou.com/aad9bee6bbac8bae76bd5a71aaa54b16/5eb77835/dl/index/1524452957/sogou_mac_47b.zip
            else:
                page_url = 'http://pinyin.sogou.com/mac/'
                # content = self.download(page_url, text=True)
                r = requests.get(page_url)
                tree = html.fromstring(r.content) # page is encoded as gbk
                url = list(tree.find_class('NowDownload')[0].iter('a'))[0].get('href')
                # http://cdn2.ime.sogou.com/61a944f90b26d4b87b494ba5467b4a9f/5eb12871/dl/index/1586258596/sogou_mac_57a.zip

        if product_name in ['wubi', 'skineditor', 'mac']:
            r = requests.head('https://pinyin.sogou.com/mac/softdown.php?r=%s' % product_name)
            url = r.headers.get('location')
            # http://cdn2.ime.sogou.com/ba1a2da9a70b1ac2b7753fbdcaa32c6a/5eb77733/dl/index/1568199881/sogou_mac_wubi_13a.zip

        self.output("Download URL for %s: %s" % (product_name, url))
        self.env["url"] = url

if __name__ == "__main__":
    processor = SogouInputURLProvider()
    processor.execute_shell()

