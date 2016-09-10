cmake_minimum_required(VERSION 3.5)
project(honeywalter)
include_directories(src)
include_directories(./libssh/include/)
file(GLOB SRCS "src/*.c")
set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ./bin)


add_executable(honeywalter ${SRCS})
link_directories(libssh/build/src/)
target_link_libraries(honeywalter ssh)
