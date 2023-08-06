import random


class Sampler:
    def __init__(self) -> None:
        pass

    def sample_random(self, threshold: float) -> bool:
        if threshold >= 1:
            return True
        if threshold <= 0:
            return False
        sample = random.uniform(0, 1)
        return sample < threshold
