#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import ssl
import urllib.request
from autopkglib import Processor, ProcessorError

__all__ = ["ClaudeCaskURLProvider"]

CASK_JSON_URL = "https://formulae.brew.sh/api/cask/claude.json"


class ClaudeCaskURLProvider(Processor):
    description = "Fetches Claude download URL and version from Homebrew Cask JSON API."
    input_variables = {}
    output_variables = {
        "url": {"description": "Latest Claude download URL from Homebrew Cask."},
        "version": {"description": "Latest Claude version (main version part)."},
    }

    def main(self):
        try:
            with urllib.request.urlopen(CASK_JSON_URL) as response:
                data = json.load(response)
        except Exception as err:
            if "CERTIFICATE_VERIFY_FAILED" not in str(err):
                raise ProcessorError(f"Failed to fetch Claude Cask JSON: {err}")
            self.output(
                "TLS certificate verification failed. Retrying Claude Cask JSON fetch without certificate validation."
            )
            try:
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(CASK_JSON_URL, context=context) as response:
                    data = json.load(response)
            except Exception as retry_err:
                raise ProcessorError(f"Failed to fetch Claude Cask JSON: {retry_err}")

        url = data.get("url")
        version_raw = data.get("version")
        if not url or not version_raw:
            raise ProcessorError("Could not find Claude URL/version in Cask JSON.")

        version = version_raw.split(",")[0] if "," in version_raw else version_raw
        self.env["url"] = url
        self.env["version"] = version
        self.output(f"Found Claude URL: {url}")
        self.output(f"Found Claude version: {version}")


if __name__ == "__main__":
    processor = ClaudeCaskURLProvider()
    processor.execute()
