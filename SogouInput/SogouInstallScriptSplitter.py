#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import stat

from autopkglib import Processor, ProcessorError

__all__ = ["SogouInstallScriptSplitter"]

class SogouInstallScriptSplitter(Processor):
    description = "Split Original install script into preinstall, and postinstall for packing as a pkg"
    input_variables = {
        "install_script": {
            "required": True,
            "description": "Path of the original install.sh"
        },
        "destination_path": {
            "required": True,
            "description": "Directory where splitted install scripts are to be stored."
        },
    }
    output_variables = {
    }

    __doc__ = description

    def write_script(self, filename, content):
        try:
            with open(filename, "w") as fileref:
                fileref.write(content)
            self.output("Created file at %s" % filename)
            os.chmod(filename, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH )
        except BaseException as err:
            raise ProcessorError("Can't create file at %s: %s"
                                 % (filename, err))

    def do_split(self, install_script, destination_path):
        try:
            with open(install_script) as fp:
                file_content = fp.read()
        except BaseException as err:
            raise ProcessorError("Can't open file at %s: %s"
                                 % (install_script, err))

        segs = re.split(r'#-+(前期工作|安装|解压词库)-+', file_content)
        if len(segs) != 7:
            raise ProcessorError("Failed splitting install script %s"
                                 % install_script)

        # 0: var definitions to be shared by all scripts
        # 1: '前期工作'
        # 2: actions to become preflight scripts
        # 3: '安装'
        # 4: actions done by munki installer
        # 5: '解压词库'
        # 6: actions to become postflight scripts

        template = '#!/bin/bash\n\n{}\n#--------------{}--------------#\n{}'

        preflight= template.format(segs[0], segs[1], segs[2]) + '\nexit 0\n'
        postflight = template.format(segs[0], segs[5], segs[6])

        self.write_script(os.path.join(destination_path, 'preflight'), preflight)
        self.write_script(os.path.join(destination_path, 'postflight'), postflight)


    def main(self):
        """Load the Install script and do the splitting"""
        # handle some defaults for archive_path and destination_path
        install_script = self.env.get("install_script")
        if not install_script:
            raise ProcessorError(
                "Expected an 'install_script' input variable but none is set!")

        destination_path = self.env.get("destination_path")
        if not destination_path:
            raise ProcessorError(
                "Expected an 'destination_path' input variable but none is set!")

        # Create the directory if needed.
        if not os.path.exists(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError as err:
                raise ProcessorError("Can't create %s: %s"
                                     % (destination_path, err.strerror))

        self.do_split(install_script, destination_path)
        self.output("Script %s splitted to %s" % (install_script, destination_path))

if __name__ == '__main__':
    PROCESSOR = SogouInstallScriptSplitter()
    PROCESSOR.execute_shell()
