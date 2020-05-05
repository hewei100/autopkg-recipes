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

        version = self.env.get('version', '')
        if version:
            if version == 'latest':
                version = ''

        if product_name == 'pinyin':
            page_url = 'http://pinyin.sogou.com/mac/'
            # content = self.download(page_url, text=True)
            r = requests.get(page_url)
            tree = html.fromstring(r.content) # page is encoded as gbk
            url = list(tree.find_class('NowDownload')[0].iter('a'))[0].get('href')
            # http://cdn2.ime.sogou.com/61a944f90b26d4b87b494ba5467b4a9f/5eb12871/dl/index/1586258596/sogou_mac_57a.zip
            if version:
                url = re.sub(r'(?<=mac_)57a', version, url)

        elif product_name == 'wubi' or product_name == 'skineditor':
            url = 'https://pinyin.sogou.com/mac/softdown.php?r=%s' % product_name
            #if version:
            #    url += '&v=' + version

        self.output("Download URL for %s: %s" % (product_name, url))
        self.env["url"] = url

if __name__ == "__main__":
    processor = SogouInputURLProvider()
    processor.execute_shell()

