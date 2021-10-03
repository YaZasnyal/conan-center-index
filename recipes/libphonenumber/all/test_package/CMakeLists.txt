cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${CONAN_LIBS})
if (WITH_GEOCODER)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GEOCODER)
endif()
