cmake_minimum_required(VERSION 3.4...3.18)
set(CMAKE_CXX_STANDARD 20)

project(tiledbpypcl)

add_subdirectory(pybind11)

pybind11_add_module(tiledbpypcl
                    pypcl/point_types.hpp
                    pypcl/vector_classes.hpp
                    pypcl/point_cloud_buffers.hpp
                    pypcl/make_opaque_vectors.hpp
                    pypcl/point_cloud_from_array.hpp
                    pypcl/range_image.hpp
                    pypcl/pyramid_port.hpp
                    pypcl/main.cpp)


set(Qt5_DIR "/opt/homebrew/opt/qt@5/lib/cmake/Qt5")
find_package(PCL 1.12 REQUIRED COMPONENTS common io tracking keypoints visualization)
include_directories(${PCL_INCLUDE_DIR})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})
target_link_libraries(tiledbpypcl PRIVATE ${PCL_LIBRARIES})


# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
target_compile_definitions(tiledbpypcl
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})
