import os
import platform
import tempfile
import unittest

import pytest
import torch
import torch_tensorrt
from torch.testing._internal.common_utils import TestCase, run_tests

from ..testing_utilities import DECIMALS_OF_AGREEMENT


class TestCrossCompileSaveForWindows(TestCase):

    @unittest.skipIf(
        platform.system() != "Linux" or platform.architecture()[0] != "64bit",
        "Cross compile for windows can only be enabled on linux 64 AMD platform",
    )
    @pytest.mark.unit
    def test_cross_compile_save_for_windows(self):
        class Add(torch.nn.Module):
            def forward(self, a, b):
                return torch.add(a, b)

        model = Add().eval().cuda()
        inputs = [torch.randn(2, 3).cuda(), torch.randn(2, 3).cuda()]
        trt_ep_path = os.path.join(tempfile.gettempdir(), "trt.ep")
        try:
            torch_tensorrt.cross_compile_save_for_windows(
                model, file_path=trt_ep_path, inputs=inputs
            )
        except Exception as e:
            pytest.fail(f"unexpected exception raised: {e}")

    @unittest.skipIf(
        platform.system() != "Linux" or platform.architecture()[0] != "64bit",
        "Cross compile for windows can only be enabled on linux 64 AMD platform",
    )
    @pytest.mark.unit
    def test_dynamo_cross_compile_save_for_windows(self):
        class Add(torch.nn.Module):
            def forward(self, a, b):
                return torch.add(a, b)

        model = Add().eval().cuda()
        inputs = (torch.randn(2, 3).cuda(), torch.randn(2, 3).cuda())
        trt_ep_path = os.path.join(tempfile.gettempdir(), "trt.ep")
        exp_program = torch.export.export(model, inputs)
        try:
            torch_tensorrt.dynamo.cross_compile_save_for_windows(
                exp_program, file_path=trt_ep_path, inputs=inputs
            )
        except Exception as e:
            pytest.fail(f"unexpected exception raised: {e}")

    @unittest.skipIf(
        platform.system() != "Windows" or platform.machine != "AMD64",
        "Cross compile for windows can only be loaded on on windows AMD64 platform",
    )
    @pytest.mark.unit
    def test_load_from_windows(self):
        trt_ep_path = "tests/py/dynamo/runtime/test_data/trt.ep"
        print("lan added run the test_load_from_windows test")
        try:
            loaded_trt_module = torch.export.load(trt_ep_path)
            trt_gm = loaded_trt_module.module()
            a = torch.randn(2, 3).cuda()
            b = torch.randn(2, 3).cuda()
            trt_output = trt_gm(a, b)
            torch_output = torch.add(a, b)
            self.assert_close(trt_output, torch_output)
        except Exception as e:
            pytest.fail(f"unexpected exception raised: {e}")
