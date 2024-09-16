set -x

TORCH=$(grep "^torch" ${PWD}/py/requirements.txt)
INDEX_URL=https://download.pytorch.org/whl/${CHANNEL}/${CU_VERSION}
PLATFORM=$(python -c "import sys; print(sys.platform)")

# Install all the dependencies required for Torch-TensorRT
pip install --pre ${TORCH} --index-url ${INDEX_URL}

# Install optional torchvision required for Torch-TensorRT tests
TORCHVISION=$(grep "^torchvision" ${PWD}/tests/py/requirements.txt)
pip install --pre ${TORCHVISION} --index-url ${INDEX_URL}

# Install optional dependencies required for Torch-TensorRT tests
pip install --pre -r ${PWD}/tests/py/requirements.txt --use-deprecated legacy-resolver

# Install Torch-TensorRT
if [[ ${PLATFORM} == win32 ]]; then
    pip install ${RUNNER_ARTIFACT_DIR}/torch_tensorrt*.whl
else
    pip install /opt/torch-tensorrt-builds/torch_tensorrt*.whl
fi

echo -e "Running test script";
