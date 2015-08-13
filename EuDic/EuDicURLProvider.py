#!/usr/bin/env python

import urllib2
import xml.dom.minidom
from distutils.version import LooseVersion
from operator import itemgetter

from autopkglib import Processor, ProcessorError

__all__ = ["EuDicURLProvider"]

EUDIC_UPDATE_URL = "http://www.eudic.net/update/eudic_mac.xml"

class EuDicURLProvider(Processor):
    description = "To-do: require a 'product_name' to reuse this provider for other products from EuDic."
    input_variables = {
        }
    output_variables = {
        "version": {
            "description": "Version of the product.",
        },
        "url": {
            "description": "Download URL.",
        },
        "description": {
            "description": "Update description."
        }
    }

    __doc__ = description

    def main(self):

        def compare_version(a, b):
            return cmp(LooseVersion(a), LooseVersion(b))

        url = EUDIC_UPDATE_URL
        try:
            manifest_str = urllib2.urlopen(url).read()
        except BaseException as e:
            raise ProcessorError("Unexpected error retrieving product manifest: '%s'" % e)

        the_xml = xml.dom.minidom.parseString(manifest_str)
        channel = the_xml.getElementsByTagName('channel')[0]
        if channel:
            items = channel.getElementsByTagName('item')
            if items:
                description = items[0].getElementsByTagName('title')[0].firstChild.nodeValue
                update = items[0].getElementsByTagName('enclosure')[0]
                url = update.getAttribute('url')
                version = update.getAttribute('sparkle:shortVersionString')
                if update.hasAttribute('sparkle:version'):
                    version += '.' + update.getAttribute('sparkle:version')
  
                self.env["version"] = version
                self.env["description"] = description
                self.env["url"] = url
                self.output("Found URL %s" % self.env["url"])

if __name__ == "__main__":
    processor = EuDicURLProvider()
    processor.execute_shell()
