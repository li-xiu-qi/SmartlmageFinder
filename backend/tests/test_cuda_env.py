import torch

def test_cuda_available():
    print(f"torch version: {torch.__version__}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU数量: {torch.cuda.device_count()}")
        print(f"当前GPU: {torch.cuda.current_device()}")
        print(f"GPU名称: {torch.cuda.get_device_name(torch.cuda.current_device())}")
    else:
        print("未检测到可用的CUDA设备，模型将使用CPU。")

if __name__ == "__main__":
    test_cuda_available()
