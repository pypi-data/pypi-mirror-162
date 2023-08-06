import torch

class DisturbValue:
    def __init__(self, alpha=0.2, sigma=1e-2):
        self.alpha = alpha
        self.sigma = sigma

    def dv(self, x):
        noise = torch.normal(0, self.sigma, size=(len(x), 1))
        noise[torch.randint(0, len(x), (int(len(x)*(1-self.alpha)),))] = 0
        return x + noise
