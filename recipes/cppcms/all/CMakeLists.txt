cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Library uses CMAKE_SOURCE_DIR to find some include directories
# Adding missing includes manually here.
include_directories(${CMAKE_CURRENT_LIST_DIR}/source_subfolder)
add_subdirectory(source_subfolder)
