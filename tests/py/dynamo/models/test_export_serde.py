import unittest

import pytest
import timm
import torch
import torch_tensorrt as torchtrt
import torchvision.models as models
from torch_tensorrt.dynamo.utils import COSINE_THRESHOLD, cosine_similarity

assertions = unittest.TestCase()


@pytest.mark.unit
def test_base_full_compile(ir):
    """
    This tests export serde functionality on a base model
    which is fully TRT convertible
    """

    class MyModule(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = torch.nn.Conv2d(3, 16, 3, stride=1, bias=True)
            self.relu = torch.nn.ReLU()

        def forward(self, x):
            out = self.conv(x)
            out = self.relu(out)
            return out

    model = MyModule().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "min_block_size": 1,
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")

    # Check Pyt and TRT exported program outputs
    cos_sim = cosine_similarity(model(input), trt_exp_program(input)[0])
    assertions.assertTrue(
        cos_sim > COSINE_THRESHOLD,
        msg=f"test_base_model_full_compile TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
    )
    # Check Pyt and deserialized TRT exported program outputs
    cos_sim = cosine_similarity(model(input), deser_trt_exp_program(input)[0])
    assertions.assertTrue(
        cos_sim > COSINE_THRESHOLD,
        msg=f"test_base_model_full_compile TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
    )


@pytest.mark.unit
def test_base_full_compile_multiple_outputs(ir):
    """
    This tests export serde functionality on a base model
    with multiple outputs which is fully TRT convertible
    """

    class MyModule(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = torch.nn.Conv2d(3, 16, 3, stride=1, bias=True)
            self.relu = torch.nn.ReLU()

        def forward(self, x):
            conv = self.conv(x)
            conv = conv * 0.5
            relu = self.relu(conv)
            return conv, relu

    model = MyModule().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "min_block_size": 1,
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")
    # Check Pyt and TRT exported program outputs
    outputs_pyt = model(input)
    outputs_trt = trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_base_full_compile_multiple_outputs TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )

    # Check Pyt and deserialized TRT exported program outputs
    outputs_trt_deser = deser_trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt_deser[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_base_full_compile_multiple_outputs deserialized TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )


@pytest.mark.unit
def test_no_compile(ir):
    """
    This tests export serde functionality on a model
    which won't convert to TRT because of min_block_size=5 constraint
    """

    class MyModule(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = torch.nn.Conv2d(3, 16, 3, stride=1, bias=True)
            self.relu = torch.nn.ReLU()

        def forward(self, x):
            conv = self.conv(x)
            conv = conv * 0.5
            relu = self.relu(conv)
            return conv, relu

    model = MyModule().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "debug": True,
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")
    # Check Pyt and TRT exported program outputs
    outputs_pyt = model(input)
    outputs_trt = trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_no_compile TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )

    # Check Pyt and deserialized TRT exported program outputs
    outputs_trt_deser = deser_trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt_deser[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_no_compile deserialized TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )


@pytest.mark.unit
def test_hybrid_relu_fallback(ir):
    """
    This tests export save and load functionality on a hybrid
    model with Pytorch and TRT segments. Relu (unweighted) layer is forced to
    fallback
    """

    class MyModule(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = torch.nn.Conv2d(3, 16, 3, stride=1, bias=True)
            self.relu = torch.nn.ReLU()

        def forward(self, x):
            conv = self.conv(x)
            relu = self.relu(conv)
            mul = relu * 0.5
            return mul

    model = MyModule().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "min_block_size": 1,
        "torch_executed_ops": {"torch.ops.aten.relu.default"},
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")

    outputs_pyt = model(input)
    outputs_trt = trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_hybrid_relu_fallback TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )

    outputs_trt_deser = deser_trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt_deser[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_hybrid_relu_fallback deserialized TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )


@pytest.mark.unit
def test_resnet18(ir):
    """
    This tests export save and load functionality on Resnet18 model
    """
    model = models.resnet18().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "min_block_size": 1,
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")

    outputs_pyt = model(input)
    outputs_trt = trt_exp_program(input)
    cos_sim = cosine_similarity(outputs_pyt, outputs_trt[0])
    assertions.assertTrue(
        cos_sim > COSINE_THRESHOLD,
        msg=f"test_resnet18 TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
    )

    outputs_trt_deser = deser_trt_exp_program(input)

    cos_sim = cosine_similarity(outputs_pyt, outputs_trt_deser[0])
    assertions.assertTrue(
        cos_sim > COSINE_THRESHOLD,
        msg=f"test_resnet18 deserialized TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
    )


@pytest.mark.unit
def test_hybrid_conv_fallback(ir):
    """
    This tests export save and load functionality on a hybrid
    model where a conv (a weighted layer)  has been forced to fallback to Pytorch.
    """

    class MyModule(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = torch.nn.Conv2d(3, 16, 3, stride=1, bias=True)
            self.relu = torch.nn.ReLU()

        def forward(self, x):
            conv = self.conv(x)
            relu = self.relu(conv)
            mul = relu * 0.5
            return mul

    model = MyModule().eval().cuda()
    input = torch.randn((1, 3, 224, 224)).to("cuda")

    compile_spec = {
        "inputs": [
            torchtrt.Input(
                input.shape, dtype=torch.float, format=torch.contiguous_format
            )
        ],
        "ir": ir,
        "min_block_size": 1,
        "torch_executed_ops": {"torch.ops.aten.convolution.default"},
    }

    exp_program = torchtrt.dynamo.trace(model, **compile_spec)
    trt_exp_program = torchtrt.dynamo.compile(exp_program, **compile_spec)
    torch.export.save(trt_exp_program, "/tmp/trt.ep")
    deser_trt_exp_program = torch.export.load("/tmp/trt.ep")

    outputs_pyt = model(input)
    outputs_trt = trt_exp_program(input)

    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_hybrid_conv_fallback TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )

    outputs_trt_deser = deser_trt_exp_program(input)
    for idx in range(len(outputs_pyt)):
        cos_sim = cosine_similarity(outputs_pyt[idx], outputs_trt_deser[idx])
        assertions.assertTrue(
            cos_sim > COSINE_THRESHOLD,
            msg=f"test_hybrid_conv_fallback deserialized TRT outputs don't match with the original model. Cosine sim score: {cos_sim} Threshold: {COSINE_THRESHOLD}",
        )
