cmake_minimum_required(VERSION 3.5)
project(honeywalter)
include_directories(src)
file(GLOB SRCS "src/*.c")
set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ./bin)


add_executable(honeywalter ${SRCS})
target_link_libraries(honeywalter ssh)
