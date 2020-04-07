#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/9/11 14:19

information about this file
"""
from common import *


class Gallery(Common):
    app_name = 'Gallery'
    package = 'com.tcl.gallery'
    launch_activity = '.app.GalleryActivity'

    def setup(self):
        self.clear(self.package)
        self.start_app(self.app_name)
        self.allow_permissions()
