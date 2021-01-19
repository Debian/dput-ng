# -*- coding: utf-8 -*-
"""
FTPS Uploader implementation.
"""

import dput.uploaders.ftp

class FtpsUploader(dput.uploaders.ftp.FtpUploader):
    """
    Provides an interface to upload files through FTPS (RFC 4217), otherwise
    just the same as the ftp uploader.
    """

    def initialize(self, **kwargs):
        super().initialize(**kwargs, use_tls=True)
