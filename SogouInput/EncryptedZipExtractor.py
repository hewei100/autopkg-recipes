#!/usr/bin/python

import os
import subprocess
import shutil

from autopkglib import Processor, ProcessorError

__all__ = ["EncryptedZipExtractor"]

class EncryptedZipExtractor(Processor):
    description = "Extracts bundle ID and version of app inside SogouPinyin source dmg."
    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to an archive. Defaults to contents of the "
                           "'pathname' variable, for example as is set by "
                           "URLDownloader."
        },
        "destination_path": {
            "required": False,
            "description": "Directory where archive will be unpacked, created "
                           "if necessary. Defaults to RECIPE_CACHE_DIR/NAME."
        },
        "archive_password": {
            "required": True,
            "description": "The password of the zip file. Simply use the Unarchiver "
                           "processor for unencrypted zip files."
        },
        "purge_destination": {
            "required": False,
            "description": "Whether the contents of the destination directory "
                           "will be removed before unpacking."
        }
    }
    output_variables = {
    }

    __doc__ = description

    def main(self):
        """Unarchive a file"""
        # handle some defaults for archive_path and destination_path
        archive_path = self.env.get("archive_path", self.env.get("pathname"))
        if not archive_path:
            raise ProcessorError(
                "Expected an 'archive_path' input variable but none is set!")

        archive_password = self.env.get("archive_password")
        if not archive_password:
            raise ProcessorError(
                "Expected an 'archive_password' input variable but none is set!")

        destination_path = self.env.get(
            "destination_path",
            os.path.join(self.env["RECIPE_CACHE_DIR"], self.env["NAME"]))

        # Create the directory if needed.
        if not os.path.exists(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError as err:
                raise ProcessorError("Can't create %s: %s"
                                     % (destination_path, err.strerror))
        elif self.env.get('purge_destination'):
            for entry in os.listdir(destination_path):
                path = os.path.join(destination_path, entry)
                try:
                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)
                except OSError as err:
                    raise ProcessorError("Can't remove %s: %s"
                                         % (path, err.strerror))
        cmd = ["/usr/bin/unzip",
               "-P", archive_password,
               "-d", destination_path,
               archive_path]

        # Call command.
        try:
            self.output("Executing %s" % " ".join(cmd))
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            (_, stderr) = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                "%s execution failed with error code %d: %s"
                % (os.path.basename(cmd[0]), err.errno, err.strerror))
        if proc.returncode != 0:
            raise ProcessorError(
                "Unarchiving %s with %s failed: %s"
                % (archive_path, os.path.basename(cmd[0]), stderr))

        self.output("Unarchived %s to %s" % (archive_path, destination_path))

if __name__ == '__main__':
    PROCESSOR = EncryptedZipExtractor()
    PROCESSOR.execute_shell()
