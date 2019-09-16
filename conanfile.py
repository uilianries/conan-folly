#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration


class FollyConan(ConanFile):
    name = "folly"
    version = "2019.09.02.00"
    description = "An open-source C++ components library developed and used at Facebook"
    topics = ("conan", "folly", "facebook", "components", "core", "efficiency")
    url = "https://github.com/bincrafters/conan-folly"
    homepage = "https://github.com/facebook/folly"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"
    requires = (
        "boost/1.71.0@conan/stable",
        "double-conversion/3.1.1@bincrafters/stable",
        "gflags/2.2.1@bincrafters/stable",
        "glog/20181109@bincrafters/stable",
        "libevent/2.1.8@bincrafters/stable",
        "lz4/1.8.3@bincrafters/stable",
        "OpenSSL/1.0.2s@conan/stable",
        "zlib/1.2.11@conan/stable",
        "zstd/1.4.0@bincrafters/stable",
        "snappy/1.1.7@bincrafters/stable",
        "bzip2/1.0.8@conan/stable",
        "libsodium/1.0.18@bincrafters/stable",
        "lzma/5.2.4@bincrafters/stable",
        "libdwarf/20190505@bincrafters/stable"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
        elif self.settings.os == "Macos":
            del self.options.shared

    def configure(self):
        compiler_version = Version(self.settings.compiler.version.value)
        if self.settings.os == "Windows" and \
            self.settings.compiler == "Visual Studio" and \
            compiler_version < "15":
            raise ConanInvalidConfiguration("Folly could not be built by Visual Studio < 14")
        elif self.settings.os == "Windows" and \
            self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Folly requires a 64bit target architecture")
        elif self.settings.os == "Windows" and \
             self.settings.compiler == "Visual Studio" and \
             "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Folly could not be build with runtime MT")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "clang" and \
            compiler_version < "6.0":
            raise ConanInvalidConfiguration("Folly could not be built by Clang < 6.0")
        elif self.settings.os == "Linux" and \
            self.settings.compiler == "gcc" and \
            compiler_version < "5":
            raise ConanInvalidConfiguration("Folly could not be built by GCC < 5")
        elif self.settings.os == "Macos" and \
             self.settings.compiler == "apple-clang" and \
             compiler_version < "8.0":
            raise ConanInvalidConfiguration("Folly could not be built by apple-clang < 8.0")

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libunwind/1.3.1@bincrafters/stable")
        if self.settings.os == "Linux" or \
           self.settings.compiler == "gcc" and self.settings.os == "Windows":
            self.requires("libiberty/9.1.0@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + '-' + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file='0001-compiler-options.patch')
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self) + ["folly"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl"])
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
        if (self.settings.os == "Linux" and self.settings.compiler == "clang" and
           Version(self.settings.compiler.version.value) == "6" and self.settings.compiler.libcxx == "libstdc++") or \
           (self.settings.os == "Macos" and self.settings.compiler == "apple-clang" and
           Version(self.settings.compiler.version.value) == "9.0" and self.settings.compiler.libcxx == "libc++"):
            self.cpp_info.libs.append("atomic")
