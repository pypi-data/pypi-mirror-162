from __future__ import annotations

from functools import partial
from typing import Any, Callable, List, Sequence, TypeVar, cast

import vapoursynth as vs
from vsexprtools import PlanesT, normalise_planes, normalise_seq, to_arr
from vsutil import disallow_variable_format, disallow_variable_resolution

from .enum import RemoveGrainMode, RepairMode

__all__ = [
    'wmean_matrix', 'mean_matrix',
    'pick_func_stype',
    'norm_rmode_planes',
    'iterate'
]

core = vs.core

FINT = TypeVar('FINT', bound=Callable[..., vs.VideoNode])
FFLOAT = TypeVar('FFLOAT', bound=Callable[..., vs.VideoNode])

wmean_matrix = [1, 2, 1, 2, 4, 2, 1, 2, 1]
mean_matrix = [1, 1, 1, 1, 1, 1, 1, 1, 1]


@disallow_variable_format
@disallow_variable_resolution
def pick_func_stype(clip: vs.VideoNode, func_int: FINT, func_float: FFLOAT) -> FINT | FFLOAT:
    assert clip.format
    return func_float if clip.format.sample_type == vs.FLOAT else func_int


RModeT = TypeVar('RModeT', RemoveGrainMode, RepairMode)


def norm_rmode_planes(
    clip: vs.VideoNode, mode: int | RModeT | Sequence[int | RModeT], planes: PlanesT = None
) -> List[int]:
    assert clip.format

    modes_array = normalise_seq(to_arr(mode), clip.format.num_planes)

    planes = normalise_planes(clip, planes)

    return [
        cast(RModeT, rep if i in planes else 0) for i, rep in enumerate(modes_array, 0)
    ]


IT = TypeVar('IT')
IR = TypeVar('IR')


def iterate(base: IT, function: Callable[[IT | IR], IT | IR], count: int, *args: Any, **kwargs: Any) -> IT | IR:
    if count <= 0:
        return base

    func = partial(function, **kwargs)

    def _iterate(x: IT | IR, n: int) -> IT | IR:
        return n and _iterate(func(x, *args), n - 1) or x

    return _iterate(base, count)
