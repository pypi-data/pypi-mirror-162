

from thop import profile
import torch
def gflop(model, size):
    input = torch.randn(size)
    macs, params = profile(model, inputs=(input,))
    return macs, params

def modelParam(model):
    return sum([m.numel() for m in model.parameters()])