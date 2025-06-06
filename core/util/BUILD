load("@rules_cc//cc:defs.bzl", "cc_library")
load("@rules_pkg//:pkg.bzl", "pkg_tar")

package(default_visibility = ["//visibility:public"])

config_setting(
    name = "use_torch_whl",
    flag_values = {
        "//toolchains/dep_src:torch": "whl"
    },
)

config_setting(
    name = "sbsa",
    constraint_values = [
        "@platforms//cpu:aarch64",
    ],
    flag_values = {
        "//toolchains/dep_collection:compute_libs": "default"
    },
)

config_setting(
    name = "jetpack",
    constraint_values = [
        "@platforms//cpu:aarch64",
    ],
    flag_values = {
        "//toolchains/dep_collection:compute_libs": "jetpack"
    },
)

config_setting(
    name = "windows",
    constraint_values = [
        "@platforms//os:windows",
    ],
)

cc_library(
    name = "prelude",
    hdrs = [
        "prelude.h",
    ],
    deps = [
        ":build_info",
        ":exception",
        ":jit_util",
        ":macros",
        ":trt_util",
        "//core/util/logging",
    ],
)

cc_library(
    name = "jit_util",
    hdrs = [
        "jit_util.h",
    ],
    deps = [
        ":macros",
    ] + select({
        ":windows": ["@libtorch_win//:libtorch"],
        ":use_torch_whl": ["@torch_whl//:libtorch"],
        ":jetpack": ["@torch_l4t//:libtorch"],
        "//conditions:default": ["@libtorch"],
    }),
)

cc_library(
    name = "macros",
    hdrs = [
        "macros.h",
    ],
    deps = [
        ":exception",
        "//core/util/logging",
    ],
)

cc_library(
    name = "exception",
    srcs = [
        "Exception.cpp",
    ],
    hdrs = [
        "Exception.h",
    ],
    alwayslink = True,
)

cc_library(
    name = "build_info",
    hdrs = [
        "build_info.h",
    ],
    deps = select({
        ":windows": ["@libtorch_win//:libtorch"],
        ":use_torch_whl": ["@torch_whl//:libtorch"],
        ":jetpack": ["@torch_l4t//:libtorch"],
        "//conditions:default": ["@libtorch"],
    }),
)

cc_library(
    name = "trt_util",
    srcs = [
        "trt_util.cpp",
    ],
    hdrs = [
        "trt_util.h",
    ],
    deps = [
        ":macros",
        "//core/util/logging",
    ] + select({
        ":windows": ["@tensorrt_win//:nvinfer"],
        ":sbsa": ["@tensorrt_sbsa//:nvinfer"],
        ":jetpack": ["@tensorrt_l4t//:nvinfer"],
        "//conditions:default": ["@tensorrt//:nvinfer"],
    }) + select({
        ":windows": ["@libtorch_win//:libtorch"],
        ":use_torch_whl": ["@torch_whl//:libtorch"],
        ":jetpack": ["@torch_l4t//:libtorch"],
        "//conditions:default": ["@libtorch"],
    }),
    alwayslink = True,
)

pkg_tar(
    name = "include",
    srcs = [
        "//core/util:Exception.h",
        "//core/util:build_info.h",
        "//core/util:jit_util.h",
        "//core/util:macros.h",
        "//core/util:prelude.h",
        "//core/util:trt_util.h",
    ],
    package_dir = "core/util/",
)
