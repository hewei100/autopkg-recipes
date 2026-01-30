#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ssl
import urllib.request
from autopkglib import Processor, ProcessorError

__all__ = ["TencentMeetingCaskURLProvider"]

CASK_JSON_URL = "https://formulae.brew.sh/api/cask/tencent-meeting.json"

class TencentMeetingCaskURLProvider(Processor):
    description = "Fetches the latest Tencent Meeting download URL and version from Homebrew Cask JSON API."
    input_variables = {}
    output_variables = {
        "url": {
            "description": "Latest Tencent Meeting download URL from Homebrew Cask."
        },
        "version": {
            "description": "Latest Tencent Meeting version (main version part)."
        }
    }

    def main(self):
        try:
            with urllib.request.urlopen(CASK_JSON_URL) as response:
                data = json.load(response)
        except ssl.SSLError:
            # Fallback: try unverified context if there's an SSL verification problem
            try:
                ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(CASK_JSON_URL, context=ctx) as response:
                    data = json.load(response)
            except Exception as e:
                raise ProcessorError(f"Failed to fetch Cask JSON (SSL fallback failed): {e}")
        except Exception as e:
            raise ProcessorError(f"Failed to fetch Cask JSON: {e}")

        url = data.get("url")
        version_raw = data.get("version")
        if not url or not version_raw:
            raise ProcessorError("Could not find URL or version in Cask JSON.")

        # Use only the first part of the version (before the comma), e.g., '3.41.1.434'
        if "," in version_raw:
            version = version_raw.split(",")[0]
        else:
            version = version_raw

        self.env["url"] = url
        self.env["version"] = version
        self.output(f"Found Tencent Meeting URL: {url}")
        self.output(f"Found Tencent Meeting version: {version}")

if __name__ == "__main__":
    processor = TencentMeetingCaskURLProvider()
    processor.execute()
