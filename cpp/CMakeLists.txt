cmake_minimum_required(VERSION 3.10)

# Project name and version.
project(flock VERSION 0.0)

# Specify which C++ standard -- I think "17" here is same as "gnu++17" in Xcode 
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add source files to the executable
add_executable(flock
               main.cpp)

# Find the external GLEW and GLFW packages.
find_package(GLFW3 REQUIRED)
find_package(GLEW REQUIRED)

# In target_link_libraries(): important to use "glfw" instead of "GLFW::glfw"
# as suggested by https://stackoverflow.com/q/68871506/1991373
target_link_libraries(flock glfw GLEW::glew)
