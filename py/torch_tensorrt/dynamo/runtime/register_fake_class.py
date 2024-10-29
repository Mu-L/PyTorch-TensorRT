import base64
from typing import Any, List

import tensorrt as trt
import torch
from torch.fx.experimental.proxy_tensor import unset_fake_temporarily
from torch_tensorrt.dynamo.utils import unwrap_tensor_shape
from torch_tensorrt.logging import TRT_LOGGER


@torch.library.register_fake("tensorrt::execute_engine")  # type: ignore
def fake_tensorrt_execute_engine(inputs: List[torch.Tensor], trt_engine: Any) -> Any:
    # with unset_fake_temporarily():
    #     breakpoint()
    real_inputs = []
    # for input in inputs:
    #     real_inputs.append(
    #         torch.rand(input.shape, dtype=input.dtype, device=input.device)
    #     )

    # This will call the FakeTRTEngine.__call__ method which runs inference on real TRT engine and inputs and returns the outputs
    # The output should be fake tensors as per general understanding but we are returning real tensors as outputs here which works.
    return trt_engine.wrapped_obj(inputs)


# namespace::class_name
@torch._library.register_fake_class("tensorrt::Engine")
class FakeTRTEngine:
    def __init__(self, engine_info: List[Any]):
        self.engine = torch.classes.tensorrt.Engine(engine_info)

    @classmethod
    def __obj_unflatten__(cls, flattened_tq: Any) -> Any:
        engine_info = [info[1] for info in flattened_tq]
        engine_info[3] = base64.b64decode(engine_info[3])  # decode engine
        engine_info[4] = str(engine_info[4][0])  # input names
        engine_info[5] = str(engine_info[5][0])  # output names
        engine_info[6] = str(int(engine_info[6]))  # hw compatible
        return cls(engine_info)

    def __call__(self, inputs: List[torch.Tensor]) -> Any:
        # We use unset_fake_temporarily because if we don't it keeps calling the fake_tensorrt_execute_engine which is the caller.
        # So, we disable fake tensor mode to explicitly run inference and get outputs of TRTEngine.
        breakpoint()
        serialized_state = self.engine.__getstate__()
        serialized_engine = serialized_state[0][3]
        input_name = serialized_state[0][4]
        output_name = serialized_state[0][5]

        # TODO: Expose create_execution context method for TRTEngine to fix this
        runtime = trt.Runtime(TRT_LOGGER)
        engine = runtime.deserialize_cuda_engine(serialized_engine)
        context = engine.create_execution_context()
        for input in inputs:
            input_shape = unwrap_tensor_shape(input)
            context.set_input_shape(input_name, input_shape)
            output_shape = context.get_tensor_shape(output_name)

        # with unset_fake_temporarily():
        #     return torch.ops.tensorrt.execute_engine(inputs, self.engine)
