load("@rules_cc//cc:defs.bzl", "cc_library")

package(default_visibility = ["//visibility:public"])

config_setting(
    name = "use_torch_whl",
    flag_values = {
        "//toolchains/dep_src:torch": "whl"
    },
)

cc_library(
    name = "benchmark",
    srcs = [
        "benchmark.cpp",
        "timer.h",
    ],
    hdrs = [
        "benchmark.h",
    ],
    deps = [
        "//cpp:torch_tensorrt",
    ] + select({
        ":windows": [
            "@libtorch_win//:libtorch",
            "@libtorch_win//:caffe2",
        ],
        ":use_torch_whl": [
            "@torch_whl//:libtorch",
            "@torch_whl//:caffe2",
        ],
        ":jetpack": [
            "@torch_l4t//:libtorch",
            "@torch_l4t//:caffe2",
        ],
        "//conditions:default": [
            "@libtorch//:libtorch",
            "@libtorch//:caffe2",
        ],
    }),
)
