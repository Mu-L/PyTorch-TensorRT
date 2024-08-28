set -exou pipefail

pip install -U numpy packaging pyyaml setuptools wheel

choco install bazelisk -y

if [[ "${CU_VERSION::4}" < "cu12" ]]; then
  # replace dependencies from tensorrt-cu12-bindings/libs to tensorrt-cu11-bindings/libs
  sed -i -e "s/tensorrt-cu12==/tensorrt-${CU_VERSION::4}==/g" \
         -e "s/tensorrt-cu12-bindings==/tensorrt-${CU_VERSION::4}-bindings==/g" \
         -e "s/tensorrt-cu12-libs==/tensorrt-${CU_VERSION::4}-libs==/g" \
         pyproject.toml
fi

#curl -Lo TensorRT.zip https://developer.nvidia.com/downloads/compute/machine-learning/tensorrt/10.3.0/zip/TensorRT-10.3.0.26.Windows.win10.cuda-12.5.zip
#unzip -o TensorRT.zip -d C:/
TORCH_TORCHVISION=$(grep "^torch" py/requirements.txt)
INDEX_URL=https://download.pytorch.org/whl/${CHANNEL}/${CU_VERSION}

# Install all the dependencies required for Torch-TensorRT
pip uninstall -y torch torchvision
pip install --force-reinstall --pre ${TORCH_TORCHVISION} --index-url ${INDEX_URL}

export CUDA_HOME="$(echo ${CUDA_PATH} | sed -e 's#\\#\/#g')"
export TORCH_INSTALL_PATH="$(python -c "import torch, os; print(os.path.dirname(torch.__file__))" | sed -e 's#\\#\/#g')"

cat toolchains/ci_workspaces/MODULE.bazel.tmpl | envsubst > MODULE.bazel

cat MODULE.bazel
echo "RELEASE=1" >> ${GITHUB_ENV}
