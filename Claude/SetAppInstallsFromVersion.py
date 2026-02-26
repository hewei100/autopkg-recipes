#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import deepcopy

from autopkglib import Processor, ProcessorError

__all__ = ["SetAppInstallsFromVersion"]


class SetAppInstallsFromVersion(Processor):
    description = "Sets pkginfo installs metadata using the runtime version."
    input_variables = {
        "pkginfo": {"required": True, "description": "Munki pkginfo dictionary."},
        "version": {"required": True, "description": "Version string for installs comparison."},
        "app_path": {
            "required": False,
            "default": "/Applications/Claude.app",
            "description": "Installed app path.",
        },
        "bundle_id": {
            "required": False,
            "default": "com.anthropic.claudefordesktop",
            "description": "Installed app bundle identifier.",
        },
        "version_key": {
            "required": False,
            "default": "CFBundleShortVersionString",
            "description": "Version key to use in installs item.",
        },
    }
    output_variables = {
        "pkginfo": {"description": "Updated pkginfo dictionary with installs metadata."}
    }

    def main(self):
        pkginfo = self.env.get("pkginfo")
        if not isinstance(pkginfo, dict):
            raise ProcessorError("pkginfo must be a dictionary.")

        version = str(self.env.get("version", "")).strip()
        if not version:
            raise ProcessorError("version is required to set installs metadata.")

        version_key = str(self.env.get("version_key", "CFBundleShortVersionString")).strip()
        installs_item = {
            "type": "application",
            "path": self.env.get("app_path", "/Applications/Claude.app"),
            "CFBundleIdentifier": self.env.get("bundle_id", "com.anthropic.claudefordesktop"),
            version_key: version,
        }

        updated_pkginfo = deepcopy(pkginfo)
        updated_pkginfo["installs"] = [installs_item]
        self.env["pkginfo"] = updated_pkginfo
        self.output(
            f"Set pkginfo installs metadata for {installs_item['path']} with {version_key}={version}."
        )


if __name__ == "__main__":
    PROCESSOR = SetAppInstallsFromVersion()
    PROCESSOR.execute()
