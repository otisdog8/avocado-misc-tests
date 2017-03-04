#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright: 2017 IBM
# Author:Harish <harish@linux.vnet.ibm.com>
#

import os
import re

from avocado import Test
from avocado import main
from avocado.utils import build, distro, archive
from avocado.utils.software_manager import SoftwareManager


class Libvecpf(Test):

    """
    Libvecpf is a "Vector Printf Library"
    """

    def setUp(self):
        """
        Build libvecpf

        Source:
        http://github.com/Libvecpf/libvecpf.git
        """
        if not distro.detect().name.lower() == 'ubuntu':
            self.skip('Upsupported OS %s' % distro.detect().name.lower())

        smm = SoftwareManager()
        for package in ['gcc', 'make']:
            if not smm.check_installed(package) and not smm.install(package):
                self.error('%s is needed for the test to be run' % package)
        tarball = self.fetch_asset(
            "https://github.com/Libvecpf/libvecpf/archive/master.zip",
            expire='7d')
        archive.extract(tarball, self.srcdir)
        self.srcdir = os.path.join(self.srcdir, 'libvecpf-master')

        build.make(self.srcdir, make='./configure')
        build.make(self.srcdir)

    def test(self):
        """
        Execute self test of libvecpf library
        """
        results = build.run_make(self.srcdir, extra_args='check',
                                 ignore_status=True).stdout

        fail_list = ['FAIL', 'XFAIL', 'ERROR']
        failures = []
        for failure in fail_list:
            num_fails = re.compile(r"# %s:(.*)" %
                                   failure).findall(results)[0].strip()
            if int(num_fails):
                failures.append({failure: num_fails})

        if failures:
            self.fail('Test failed with following:%s' % failures)


if __name__ == "__main__":
    main()