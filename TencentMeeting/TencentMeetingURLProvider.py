#!/usr/bin/env python3

from requests_html import HTMLSession

import re
import xml.dom.minidom
from distutils.version import LooseVersion
from operator import itemgetter

from autopkglib import Processor, ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["TencentMeetingURLProvider"]

LANDING_PAGE_URL = "https://meeting.tencent.com/download-center.html?from=1001"
DOWNLOAD_URL = "https://down.qq.com/download/TencentMeeting_0300000000_{version}.publish.dmg"

class TencentMeetingURLProvider(URLGetter):
    input_variables = {
        "version": {
            "required": False,
            "description": "A specific version to download.",
        }
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

        requested_version = self.env.get('version', '')


        else:
        self.output("Rendering page %s" % LANDING_PAGE_URL)
        session = HTMLSession()
        r = session.get(LANDING_PAGE_URL)
        r.html.render()
        description = r.html.find('meta[name="description"]')[0].attrs['content']
        version_str = r.html.find('#mac-version')[0]
        self.output("Found: %s" % version_str)
        version = re.sub(r'(^[^\d]+)', '', version_str)

        if requested_version and requested_version != 'latest':
            version = requested_version

        url = DOWNLOAD_URL.format(version=version)

        self.env["version"] = version
        self.env["description"] = description
        self.env["url"] = url

if __name__ == "__main__":
    processor = TencentMeetingURLProvider()
    processor.execute_shell()
