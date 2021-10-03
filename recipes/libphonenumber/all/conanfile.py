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
    exports_sources = ["patches/**"]
    options = {
        "shared": [True, False], 
        "fPIC": [True, False], 
        "without_geocoder": [True, False], # don't build offline geocoder library
        "use_boost": [True, False],
        }
        # TODO: Add USE_ICU_REGEXP option
    default_options = {
        "shared": False, 
        "fPIC": True, 
        "without_geocoder": False,
        "use_boost": False,
        }
    topics = ("conan", "phonenumber", "libphonenumber", "google")

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    build_requires = list()

    def requirements(self):
        self.requires("protobuf/[>=3.6.1]")
        self.requires("icu/[>=48]")
        self.requires("gtest/[>=1.6.0]")
        if self.settings.os == 'Windows' and self.settings.compiler == 'Visual Studio':
            self.build_requires += ('dirent/[>=1.23.2]',)
        if self.options.use_boost:
            self.requires('boost/[>=1.44.0]')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            # We have to use boost for threading support on windows
            self.options.use_boost = True
            # TODO: Add posix thread support on mingw

    def source(self):
        tools.get("{homepage}/archive/v{version}.zip".format(homepage=self.homepage, version=self.version))
        os.rename("libphonenumber-" + self.version, self.source_subfolder)

    def _fix_windows(self, cmake):
        cmake.definitions["GTEST_INCLUDE_DIR"] = self.deps_cpp_info["gtest"].rootpath + '/include'
        cmake.definitions["GTEST_LIB"] = self.deps_cpp_info["gtest"].rootpath + '/lib/gtest.lib'    
        if self.settings.compiler == 'Visual Studio':
            direntInclude = os.path.join(self.deps_cpp_info["dirent"].rootpath, 'include')
            cmake.definitions["CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES"] = direntInclude
        cmake.definitions["PROTOBUF_INCLUDE_DIR"] = self.deps_cpp_info["protobuf"].rootpath + '/include'
        cmake.definitions["PROTOBUF_LIB"] = self.deps_cpp_info["protobuf"].rootpath + '/lib/libprotobuf.lib'
        cmake.definitions["PROTOC_BIN"] = self.deps_cpp_info["protobuf"].rootpath + '/bin/protoc.exe'
        libprefix = ''
        if not self.options['icu'].shared:
            cmake.definitions["DEFINE_ICU_STATIC"] = 'ON'
            libprefix += 's'
        if self.settings.build_type == "Debug": libprefix += 'd'
        cmake.definitions["ICU_I18N_INCLUDE_DIR"] = self.deps_cpp_info["icu"].rootpath + "/include"
        cmake.definitions["ICU_I18N_LIB"] = self.deps_cpp_info["icu"].rootpath + "/lib/{}icuin.lib".format(libprefix)
        cmake.definitions["ICU_UC_INCLUDE_DIR"] = self.deps_cpp_info["icu"].rootpath + "/include"
        cmake.definitions["ICU_UC_LIB"] = self.deps_cpp_info["icu"].rootpath + "/lib/{}icuuc.lib".format(libprefix)
        cmake.definitions["ICU_DATA_LIB"] = self.deps_cpp_info["icu"].rootpath + "/lib/{}icudt.lib".format(libprefix)
        if not self.options['boost'].shared:
            cmake.definitions["DEFINE_BOOST_STATIC"] = 'ON'
        if self.options['protobuf'].shared:
            cmake.definitions["DEFINE_PROTOBUF_SHARED"] = 'ON'

    def _fix_linux(self, cmake):
        cmake.definitions["CMAKE_PREFIX_PATH"] = ";".join([ self.deps_cpp_info["gtest"].rootpath , self.deps_cpp_info["protobuf"].rootpath , self.deps_cpp_info["icu"].rootpath ])
        cmake.definitions["GTEST_INCLUDE_DIR"] = self.deps_cpp_info["gtest"].rootpath + '/include'
        libsuffix = ('so' if self.options['gtest'].shared else 'a')
        cmake.definitions["GTEST_LIB"] = self.deps_cpp_info["gtest"].rootpath + '/lib/libgtest.{}'.format(libsuffix)
        libsuffix = ('so' if self.options['protobuf'].shared else 'a')
        cmake.definitions["PROTOBUF_INCLUDE_DIR"] = self.deps_cpp_info["protobuf"].rootpath + '/include'
        cmake.definitions["PROTOBUF_LIB"] = self.deps_cpp_info["protobuf"].rootpath + '/lib/libprotobuf.{}'.format(libsuffix)
        cmake.definitions["PROTOC_BIN"] = self.deps_cpp_info["protobuf"].rootpath + '/bin/protoc'
        libsuffix = ('so' if self.options['icu'].shared else 'a')
        cmake.definitions["ICU_I18N_INCLUDE_DIR"] = self.deps_cpp_info["icu"].rootpath + "/include"
        cmake.definitions["ICU_I18N_LIB"] = self.deps_cpp_info["icu"].rootpath + "/lib/libicui18n.{}".format(libsuffix)
        cmake.definitions["ICU_UC_INCLUDE_DIR"] = self.deps_cpp_info["icu"].rootpath + "/include"
        cmake.definitions["ICU_UC_LIB"] = self.deps_cpp_info["icu"].rootpath + "/lib/libicuuc.{}".format(libsuffix)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_BOOST"] = "ON" if self.options.use_boost else "OFF"
        cmake.definitions["BUILD_GEOCODER"] = "ON" if not self.options.without_geocoder else "OFF"
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        if self.settings.os == 'Windows':
            self._fix_windows(cmake)
        else:
            self._fix_linux(cmake)
        cmake.configure(source_folder=os.path.join(self.source_subfolder, "cpp"), build_folder=self.build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        include_folder = os.path.join(self.source_subfolder, "cpp/src")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        if self.options.shared == True:
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
