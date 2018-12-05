#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
from bincrafters import build_template_default


if __name__ == "__main__":
    shared_option_name = False if platform.system() == "Windows" or platform.system() == "Darwin" else "folly:shared"
    builder = build_template_default.get_builder(pure_c=False, shared_option_name=shared_option_name)
    if platform.system() == "Darwin":
        builder.update_build_if(lambda build: build.settings["compiler"] == "apple-clang" and build.settings["compiler.version"] == "9.0", new_settings={"compiler.libcxx": "libstdc++"})
    builder.run()
