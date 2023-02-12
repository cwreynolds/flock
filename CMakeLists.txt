cmake_minimum_required(VERSION 3.10)

# Project name and version.
project(flock VERSION 0.0)

# Specify which C++ standard -- I think "17" here is same as "gnu++17" in Xcode 
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# # Rewrite Version.h using Version.h.in as a template.
# configure_file(Version.h.in Version.h)

# Add source files to the executable
add_executable(flock
               main.cpp)

# Configured Version.h file will be written into the binary tree, so add that
# directory to the list of paths to search for include files.
# (TODO Does this mean we end up with two copies of Version.h?)
target_include_directories(flock PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           )

# Find the external OpenCV package, add paths for includes and libraries.

# find_package(OpenCV REQUIRED )
# target_link_libraries(texsyn ${OpenCV_LIBS})
# target_include_directories(texsyn PUBLIC "${OpenCV_INCLUDE_DIRS}" )

# find_package(GLEW REQUIRED )
find_package(glew REQUIRED )
target_link_libraries(flock ${GLEW_LIBS})
target_include_directories(flock PUBLIC "${GLEW_INCLUDE_DIRS}" )

# find_package(GLFW REQUIRED )
find_package(glfw REQUIRED )
target_link_libraries(flock ${GLFW_LIBS})
target_include_directories(flock PUBLIC "${GLFW_INCLUDE_DIRS}" )

