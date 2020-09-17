#!/usr/bin/env python3

from requests_html import AsyncHTMLSession

import re
from distutils.version import LooseVersion

from autopkglib import Processor, ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["TencentMeetingURLProvider"]

LANDING_PAGE_URL = "https://meeting.tencent.com/download-center.html?from=1001"
#DOWNLOAD_URL = "https://down.qq.com/download/TencentMeeting_0300000000_{version}.publish.dmg"
DOWNLOAD_PAGE_URL = "https://meeting.tencent.com/download-mac.html?from=1001&fromSource=1"

class TencentMeetingURLProvider(URLGetter):
    description = "Render Tencent Meeting client download page to retrive latest version string for composing download URL."
    input_variables = {
#         "version": {
#             "required": False,
#             "description": "A specific version to download.",
#         }
    }
    output_variables = {
        "version": {
            "description": "Latest version of the product.",
        },
        "url": {
            "description": "Download URL.",
        },
#         "description": {
#             "description": "Update description."
#         }
    }

    __doc__ = description

    def main(self):

#         requested_version = self.env.get('version', '')
        user_agent = self.env.get('user-agent', '')

        asession = AsyncHTMLSession()

        def reqeust_callback(req):
            if '/updatecdn.meeting.qq.com/' in req.url:
                 self.env["url"] = req.url

        async def get_version_str():
            r = await asession.get(LANDING_PAGE_URL, headers={'User-agent': user_agent})
            await r.html.arender()
            self.env["version"] = r.html.xpath('//*[@id="mac-version__value"]/text()')[0]

        async def get_download_url():
            r = await asession.get(DOWNLOAD_PAGE_URL, headers={'User-agent': user_agent})
#             script = r.html.find('.download-msg a')[0].attrs.get('onclick')
            await r.html.arender(keep_page=True)
            r.html.page.on('request', reqeust_callback)

        asession.run(get_version_str, get_download_url)

#         results = asession.run(get_version_str, get_download_url)
#         urls, version = results

#         self.env["version"] = version
#         self.env["description"] = description
#         self.env["url"] = urls.pop()

if __name__ == "__main__":
    processor = TencentMeetingURLProvider()
    processor.execute_shell()
