import os
from conans import ConanFile, tools, CMake
from conans.errors import ConanException


class LibphonenumberConan(ConanFile):
    name = "libphonenumber"
    description = "Google's common C++ library for parsing, formatting, and validating international phone numbers."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/libphonenumber"
    license = "Apache"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False], 
        "geocoder": [True, False], # build offline geocoder
        "use_boost": [True, False], # use boost
        }
    default_options = {
        "shared": False, 
        "fPIC": True, 
        "geocoder": True,
        "use_boost": False,
        }
    topics = ("conan", "phonenumber", "libphonenumber", "google")

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    build_requires = (
        "gtest/[>=1.6.0]",
    )

    def requirements(self):
        self.requires("protobuf/[>=3.6.1]")
        self.requires("icu/[>=50]")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if self.options.use_boost:
            self.requires('boost/[>=1.44.0]')
            self.options["boost"].shared = self.options.shared
        if self.options.shared:
            self.options["protobuf"].shared = True
            self.options["icu"].shared = True

    def source(self):
        tools.get("{homepage}/archive/v{version}.zip".format(homepage=self.homepage, version=self.version))
        os.rename("libphonenumber-" + self.version, self.source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        
        cmake.definitions["CMAKE_PREFIX_PATH"] = ";".join([ self.deps_cpp_info["gtest"].rootpath , self.deps_cpp_info["protobuf"].rootpath , self.deps_cpp_info["icu"].rootpath ])
        if self.options.use_boost:
            cmake.definitions["CMAKE_PREFIX_PATH"] = cmake.definitions["CMAKE_PREFIX_PATH"] + ";" + self.deps_cpp_info["boost"].rootpath
        cmake.definitions["USE_BOOST"] = "ON" if self.options.use_boost else "OFF"
        cmake.definitions["BUILD_GEOCODER"] = "ON" if self.options.geocoder else "OFF"

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(source_folder=os.path.join(self.source_subfolder, "cpp"), build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        if self.options.shared == True:
            cmake.build(target='phonenumber-shared')
            if self.options.geocoder == True:
                cmake.build(target='geocoding-shared')
        else:
            cmake.build(target='phonenumber')
            if self.options.geocoder == True:
                cmake.build(target='geocoding')

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        include_folder = os.path.join(self.source_subfolder, "cpp/src")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        if self.options.shared == True:
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
