"""Type stubs for the kdtree module

kdtree is distributed as a single-file module. Type information is therefore
shipped as this stub file, which is installed next to kdtree.py.
"""

from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from typing import Any, Generic, ParamSpec, Protocol, Self, TypeVar, overload

__author__: str
__version__: str
__website__: str
__license__: str

class _Point(Protocol):
    """Anything that can be used as a point: it has a length and its
    coordinates can be accessed by index"""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int, /) -> Any: ...

_T = TypeVar("_T")
_P = TypeVar("_P", bound=_Point)
_Q = TypeVar("_Q", bound=_Point)
_P_contra = TypeVar("_P_contra", contravariant=True)
_Q_contra = TypeVar("_Q_contra", contravariant=True)
_D_co = TypeVar("_D_co", covariant=True)
_N = TypeVar("_N", bound=Node[Any])
_D = TypeVar("_D", bound=_Distance)
_R = TypeVar("_R")
_Params = ParamSpec("_Params")

class _Distance(Protocol):
    """A distance value: search_knn() negates distances and compares them"""

    def __neg__(self) -> Self: ...
    def __lt__(self, other: Any, /) -> bool: ...
    def __gt__(self, other: Any, /) -> bool: ...

class _DistFunc(Protocol[_P_contra, _Q_contra, _D_co]):
    """A distance function, always called as dist(a, b, axis=axis)

    a is a point stored in the tree, b is the point that is searched for."""

    def __call__(
        self, a: _P_contra, b: _Q_contra, /, *, axis: int | None
    ) -> _D_co: ...

class Node(Generic[_T]):
    data: _T | None
    left: Self | None
    right: Self | None
    def __init__(
        self,
        data: _T | None = None,
        left: Self | None = None,
        right: Self | None = None,
    ) -> None: ...
    @property
    def is_leaf(self) -> bool: ...
    def preorder(self) -> Iterator[Self]: ...
    def inorder(self) -> Iterator[Self]: ...
    def postorder(self) -> Iterator[Self]: ...
    @property
    def children(self) -> Iterator[tuple[Self, int]]: ...
    def set_child(self, index: int, child: Self | None) -> None: ...
    def height(self) -> int: ...
    def get_child_pos(self, child: Node[Any]) -> int | None: ...
    def __nonzero__(self) -> bool: ...
    def __bool__(self) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

def require_axis(f: Callable[_Params, _R]) -> Callable[_Params, _R]: ...

class KDNode(Node[_P]):
    axis: int | None
    sel_axis: Callable[[int], int] | None
    dimensions: int | None
    def __init__(
        self,
        data: _P | None = None,
        left: Self | None = None,
        right: Self | None = None,
        axis: int | None = None,
        sel_axis: Callable[[int], int] | None = None,
        dimensions: int | None = None,
    ) -> None: ...
    def add(self, point: _P) -> Self: ...
    def create_subnode(self, data: _P | None) -> Self: ...
    def find_replacement(self) -> tuple[Self | None, Self]: ...
    def should_remove(self, point: _Point, node: KDNode[Any] | None) -> bool: ...
    def remove(self, point: _Point, node: KDNode[Any] | None = None) -> Self: ...
    @property
    def is_balanced(self) -> bool: ...
    def rebalance(self) -> KDNode[_P]: ...
    def axis_dist(self, point: _Point, axis: int) -> float: ...
    def dist(self, point: _Point, axis: int | None = None) -> float: ...
    @overload
    def search_knn(
        self, point: _Point, k: int, dist: None = None
    ) -> list[tuple[Self, float]]: ...
    @overload
    def search_knn(
        self, point: _Q, k: int, dist: _DistFunc[_P, _Q, _D]
    ) -> list[tuple[Self, _D]]: ...
    @overload
    def search_nn(self, point: _Point, dist: None = None) -> tuple[Self, float]: ...
    @overload
    def search_nn(
        self, point: _Q, dist: _DistFunc[_P, _Q, _D]
    ) -> tuple[Self, _D]: ...
    def search_nn_dist(self, point: _Point, distance: float) -> list[_P]: ...
    def range_search(self, top_left: _Point, bottom_right: _Point) -> list[Self]: ...
    def is_valid(self) -> bool: ...
    def extreme_child(
        self,
        sel_func: Callable[..., Any],
        axis: int,
    ) -> tuple[Self, Self | None] | tuple[None, None]: ...

@overload
def create(
    point_list: None = None,
    *,
    dimensions: int,
    axis: int = 0,
    sel_axis: Callable[[int], int] | None = None,
) -> KDNode[Any]: ...
@overload
def create(
    point_list: None,
    dimensions: int,
    axis: int = 0,
    sel_axis: Callable[[int], int] | None = None,
) -> KDNode[Any]: ...
@overload
def create(
    point_list: Sequence[_P],
    dimensions: int | None = None,
    axis: int = 0,
    sel_axis: Callable[[int], int] | None = None,
) -> KDNode[_P]: ...
@overload
def create(
    # without dimensions, they are taken from point_list[0]. Iterators are
    # not supported, as the dimensionality check consumes them
    point_list: Collection[_P],
    dimensions: int,
    axis: int = 0,
    sel_axis: Callable[[int], int] | None = None,
) -> KDNode[_P]: ...
@overload
def check_dimensionality(
    point_list: Sequence[_Point], dimensions: int | None = None
) -> int: ...
@overload
def check_dimensionality(point_list: Iterable[_Point], dimensions: int) -> int: ...
def level_order(tree: _N, include_all: bool = False) -> Iterator[_N]: ...
def visualize(
    tree: Node[Any],
    max_level: int = 100,
    node_width: int = 10,
    left_padding: int = 5,
) -> None: ...
