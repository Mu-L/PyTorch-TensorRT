load("@rules_cc//cc:defs.bzl", "cc_test")
load("//tests/core/lowering:lowering_test.bzl", "lowering_test")

config_setting(
    name = "use_torch_whl",
    flag_values = {
        "//toolchains/dep_src:torch": "whl"
    },
)

config_setting(
    name = "windows",
    constraint_values = [
        "@platforms//os:windows",
    ],
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


lowering_test(
    name = "test_linear_to_addmm",
)

cc_test(
    name = "test_module_fallback_passes",
    srcs = ["test_module_fallback_passes.cpp"],
    data = [
        "//tests/modules:jit_models",
    ],
    deps = [
        "//tests/util",
        "@googletest//:gtest_main",
    ] + select({
        ":windows": ["@libtorch_win//:libtorch"],
	":jetpack": ["@torch_l4t//:libtorch"],
	"//conditions:default": ["@libtorch"],
    }),
)

lowering_test(
    name = "test_autocast_long_inputs",
)

lowering_test(
    name = "test_conv_pass",
)

lowering_test(
    name = "test_device_casting",
)

lowering_test(
    name = "test_exception_elimination_pass",
)

lowering_test(
    name = "test_remove_contiguous_pass",
)

lowering_test(
    name = "test_remove_dropout_pass",
)

lowering_test(
    name = "test_reduce_to_pass",
)

lowering_test(
    name = "test_reduce_gelu",
)

lowering_test(
    name = "test_reduce_remainder",
)

lowering_test(
    name = "test_remove_detach_pass",
)

lowering_test(
    name = "test_remove_unnecessary_casts",
)

lowering_test(
    name = "test_view_to_reshape_pass",
)

lowering_test(
    name = "test_operator_aliasing_pass",
)

lowering_test(
    name = "test_silu_to_sigmoid_multiplication",
)

lowering_test(
    name = "test_unpack_hardsigmoid",
)

lowering_test(
    name = "test_unpack_hardswish",
)

lowering_test(
    name = "test_unpack_reduce_ops",
)

lowering_test(
    name = "test_rewrite_inputs_with_params",
)

lowering_test(
    name = "test_replace_aten_pad_pass",
)

lowering_test(
    name = "test_tile_to_repeat_pass",
)

test_suite(
    name = "lowering_tests",
    tests = [
        ":test_autocast_long_inputs",
        ":test_conv_pass",
        ":test_device_casting",
        ":test_exception_elimination_pass",
        ":test_linear_to_addmm",
        ":test_module_fallback_passes",
        ":test_operator_aliasing_pass",
        ":test_reduce_gelu",
        ":test_reduce_remainder",
        ":test_reduce_to_pass",
        ":test_remove_contiguous_pass",
        ":test_remove_detach_pass",
        ":test_remove_dropout_pass",
        ":test_remove_unnecessary_casts",
        ":test_replace_aten_pad_pass",
        ":test_rewrite_inputs_with_params",
        ":test_tile_to_repeat_pass",
        ":test_unpack_hardsigmoid",
        ":test_unpack_hardswish",
        ":test_unpack_reduce_ops",
        ":test_view_to_reshape_pass",
    ],
)
