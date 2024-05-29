#!/usr/bin/env python3

#from requests_html import AsyncHTMLSession
#from requests_html import HTMLSession

import sys, os, logging, re, time, json
#from distutils.version import LooseVersion
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener


from autopkglib import Processor, ProcessorError
from autopkglib.URLGetter import URLGetter

__all__ = ["TencentMeetingURLProvider"]

#LANDING_PAGE_URL = "https://meeting.tencent.com/download-center.html?from=1001"
LANDING_PAGE_URL = "https://meeting.tencent.com/download/"
#DOWNLOAD_URL = "https://down.qq.com/download/TencentMeeting_0300000000_{version}.publish.dmg"
#DOWNLOAD_PAGE_URL = "https://meeting.tencent.com/download-mac.html?from=1001&fromSource=1"
DOWNLOAD_PAGE_URL = "https://updatecdn.meeting.qq.com/cos/7861cf367f7764fc531090effa381b3c/TencentMeeting_0300000000_3.24.3.401.publish.arm64.officialwebsite.dmg"
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.28.10 (KHTML, like Gecko) Version/6.0.3 Safari/536.28.10'

class MyListener(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("Before navigate to %s" % url, file=sys.stderr)
    def after_navigate_to(self, url, driver):
        print("After navigate to %s" % url, file=sys.stderr)
    def after_execute_script(self, script, driver):
        print("After execute script: %s" % script, file=sys.stderr)

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
        self.env["description"] = self.description
        ua = self.env.get('USER_AGENT', USER_AGENT)

        browser = webdriver.Safari()
        #browser = EventFiringWebDriver(browser, MyListener())
        browser.get(LANDING_PAGE_URL)
        #mac_tab = browser.find_element(By.CLASS_NAME, 'mt-download-card-mini macos')

        version_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,'mt-download-card-mini__tit-version'))
        )
        time.sleep(1)

        browser.execute_script("""
        (function(){
            var orig = window.XMLHttpRequest.prototype.send;
            window.XMLHttpRequest.prototype.send = function() {
                if ( this.aegisUrl && this.aegisUrl.includes('/web-service/query-download-info') ) {
                    window.XMLHttpRequest.prototype.send = orig;
                    var req = new XMLHttpRequest();
                    req.open('GET', this.aegisUrl, false);
                    var r = req.send();
                    if ( req.status == '200' ) {
                        var resp = JSON.parse(req.responseText);
                        var info = resp['info-list'][0];
                        var el = document.getElementById('apple');
                        el.setAttribute('data-version', info.version);
                        el.setAttribute('data-download-url', info.url);
                    }
                    return r;
                }
                return orig.apply(this, arguments);
            }
        }());
        """);

        version_str = version_element.text
        print("=== Got version string: %s" % version_str, file=sys.stderr)
        self.env["version"] = re.sub(r'(^[^\d]+)', '', version_str)

        ActionChains(browser).move_to_element(version_element).click().perform()
        arm64_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID,'apple'))
        )
        time.sleep(1)
        ActionChains(browser).move_to_element(arm64_element).click().perform()
        time.sleep(2)

        version = arm64_element.get_attribute('data-version')
        if version:
            print("=== Got version: %s" % version, file=sys.stderr)
            self.env['version'] = version

        download_url = arm64_element.get_attribute('data-download-url')
        if download_url:
            print("=== Got download url: %s" % download_url, file=sys.stderr)
            self.env['url'] = download_url

        browser.close()

if __name__ == "__main__":
    processor = TencentMeetingURLProvider()
    processor.execute_shell()


#
# debug: /usr/local/munki/munki-python
#
"""
import re
from requests_html import AsyncHTMLSession, HTMLSession

LANDING_PAGE_URL = "https://meeting.tencent.com/download/"
DOWNLOAD_PAGE_URL = "https://updatecdn.meeting.qq.com/cos/2012f9451007318aea154d31ae6ff91c/TencentMeeting_0300000000_3.10.7.413.publish.x86_64.dmg"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.28.10 (KHTML, like Gecko) Version/6.0.3 Safari/536.28.10'

session = HTMLSession()
r = session.get(LANDING_PAGE_URL, headers={'User-agent': user_agent})
r.html.render(reload=True)
version_str = r.html.xpath('//*[@class="mt-download-card-mini macos"]//*[@class="mt-download-card-mini__tit-version"]/text()')[0]
re.sub(r'(^[^\d]+)', '', version_str)

#var document.getElementById('apple').setAttribute('data-url', this.aegisUrl);


async def get_ver():
    r = await asession.get(LANDING_PAGE_URL, headers={'User-agent': user_agent})
    await r.html.arender(reload=True)
    version_str = r.html.xpath('//*[@class="mt-download-card-mini macos"]//*[@class="mt-download-card-mini__tit-version"]/text()')[0]
    return "version: %s" % re.sub(r'(^[^\d]+)', '', version_str)

async def get_url():
    r = await asession.get(DOWNLOAD_PAGE_URL, headers={'User-agent': user_agent})
    await r.html.arender(keep_page=True)
    #r.html.page.on('request', reqeust_callback)
    r.html.page.on('workercreated', lambda worker: print('Worker created:', worker.url))
    return("done")

AsyncHTMLSession().run(get_ver, get_url)

"""
