from copy import deepcopy
from typing import Callable
from functools import wraps
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, PolynomialLR, SequentialLR

SCHEDULER = {}
def register_method(fn: Callable):
    key = fn.__name__
    if key in SCHEDULER:
        raise ValueError(f"An entry is already registered under the name '{key}'.")
    SCHEDULER[key] = fn
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper

def de_lrf_ratio(lrf_ratio):
    if isinstance(lrf_ratio, str): lrf_ratio = eval(lrf_ratio)
    return 0.1 if lrf_ratio is None else lrf_ratio

@register_method
def linear(optimizer, warm_ep, epochs, lr0, lrf_ratio):
    scheduler = SequentialLR(
        optimizer = optimizer,
        schedulers=[
            LinearLR(optimizer, start_factor=0.1, end_factor=1, total_iters=warm_ep),
            LinearLR(optimizer, start_factor=1, end_factor=de_lrf_ratio(lrf_ratio), total_iters=epochs)
        ],
        milestones=[warm_ep,]
    )
    return scheduler

@register_method
def cosine(optimizer, warm_ep, epochs, lr0, lrf_ratio):
    scheduler = SequentialLR(
        optimizer=optimizer,
        schedulers=[
            LinearLR(optimizer, start_factor=0.1, end_factor=1, total_iters=warm_ep),
            CosineAnnealingLR(optimizer, T_max=epochs, eta_min=de_lrf_ratio(lrf_ratio) * lr0, )
        ],
        milestones=[warm_ep, ]
    )
    return scheduler

def create_Scheduler(scheduler, optimizer, warm_ep, epochs, lr0, lrf_ratio):
    return SCHEDULER[scheduler](optimizer, warm_ep, epochs, lr0, lrf_ratio)