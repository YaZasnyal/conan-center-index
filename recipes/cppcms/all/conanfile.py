from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CppCmsConan(ConanFile):
    name = "cppcms"
    description = "CppCMS - High Performance C++ Web Framework"
    topics = ("rest", "http-server")
    license = "MIT"
    homepage = "http://cppcms.com/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypt_backend": ["openssl", "grypt", None],
        "with_fastcgi": [True, False],
        "with_scgi": [True, False],
        "with_http": [True, False],
        "with_cache": [True, False],
        "with_tcp_cache": [True, False],
        "with_gzip": [True, False],
        "with_icu": [True, False],
        "with_iconv": [True, False],
        #"with_stlport": [True, False], # Not in cci
        "with_libcxx": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypt_backend": "openssl",
        "with_fastcgi": True,
        "with_scgi": True,
        "with_http": True,
        "with_cache": True,
        "with_tcp_cache": True,
        "with_gzip": True,
        "with_icu": True,
        "with_iconv": True,
        #"with_stlport": False, # Not in cci
        "with_libcxx": False,
        }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _package_folder(self):
        return self.folders.base_package

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            self.options.with_iconv = False # This value is default False on Windows only

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], 
                  destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        if (self.options.crypt_backend == "openssl"):
            self.requires("openssl/1.1.1l")
        elif (self.options.crypt_backend == "grypt"):
            self.requires("libgcrypt/1.8.4")
        if (self.options.with_gzip):
            self.requires("zlib/1.2.11")
        if (self.options.with_icu):
            self.requires("icu/70.1")
        if (self.options.with_iconv):
            self.requires("libiconv/1.16")
        self.requires("pcre/8.45")

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "11")
            if (tools.Version(self.settings.compiler.cppstd) >= 17):
                raise ConanInvalidConfiguration("Unable to build this library with 'compiler.cppstd >= 17'")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        yes_no = lambda v: "ON" if v else "OFF"
        self._cmake.definitions["DISABLE_SHARED"] = yes_no(not self.options.shared)
        self._cmake.definitions["DISABLE_STATIC"] = yes_no(self.options.shared)
        self._cmake.definitions["DISABLE_GCRYPT"] = yes_no(self.options.crypt_backend != "grypt")
        self._cmake.definitions["DISABLE_OPENSSL"] = yes_no(self.options.crypt_backend != "openssl")
        self._cmake.definitions["DISABLE_FCGI"] = yes_no(not self.options.with_fastcgi)
        self._cmake.definitions["DISABLE_SCGI"] = yes_no(not self.options.with_scgi)
        self._cmake.definitions["DISABLE_HTTP"] = yes_no(not self.options.with_http)
        self._cmake.definitions["DISABLE_CACHE"] = yes_no(not self.options.with_cache)
        self._cmake.definitions["DISABLE_TCPCACHE"] = yes_no(not self.options.with_tcp_cache)
        self._cmake.definitions["DISABLE_GZIP"] = yes_no(not self.options.with_gzip)
        # self._cmake.definitions["USE_STLPORT"] = yes_no(self.options.with_stlport) # Not in cci
        self._cmake.definitions["DISABLE_ICU_LOCALE"] = yes_no(not self.options.with_icu)
        self._cmake.definitions["DISABLE_ICONV"] = yes_no(not self.options.with_iconv)
        self._cmake.definitions["USE_LIBCXX"] = yes_no(self.options.with_libcxx)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.TXT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "Dbghelp"]
        
        # Export path for template compiler utility
        bin_path = os.path.join(self._package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
