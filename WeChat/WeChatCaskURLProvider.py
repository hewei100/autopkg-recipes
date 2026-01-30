#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ssl
import urllib.request
from autopkglib import Processor, ProcessorError

__all__ = ["WeChatCaskURLProvider"]

CASK_JSON_URL = "https://formulae.brew.sh/api/cask/wechat.json"

# Bypass SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

class WeChatCaskURLProvider(Processor):
    description = "Fetches the latest WeChat download URL and version from Homebrew Cask JSON API."
    input_variables = {}
    output_variables = {
        "url": {
            "description": "Latest WeChat download URL from Homebrew Cask."
        },
        "version": {
            "description": "Latest WeChat version from Homebrew Cask."
        }
    }

    def main(self):
        try:
            with urllib.request.urlopen(CASK_JSON_URL) as response:
                data = json.load(response)
        except Exception as e:
            raise ProcessorError(f"Failed to fetch Cask JSON: {e}")

        url = data.get("url")
        version_raw = data.get("version")
        if not url or not version_raw:
            raise ProcessorError("Could not find URL or version in Cask JSON.")

        # Use only the first part of the version (before the comma), e.g., '4.1.7.31'
        if "," in version_raw:
            version = version_raw.split(",")[0]
        else:
            version = version_raw

        self.env["url"] = url
        self.env["version"] = version
        self.output(f"Found WeChat URL: {url}")
        self.output(f"Found WeChat version: {version}")

if __name__ == "__main__":
    processor = WeChatCaskURLProvider()
    processor.execute()
