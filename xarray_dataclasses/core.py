__all__ = ["dataarrayclass", "asdataarray"]


# standard library
from dataclasses import dataclass, Field, _DataclassParams
from typing import Any, Callable, Dict, Optional, Union


# third-party packages
import numpy as np
import xarray as xr
from typing_extensions import Protocol
from .field import Kind, set_fields


# type hints
class DataClass(Protocol):
    """Type hint for dataclasses."""

    __dataclass_fields__: Dict[str, Field]
    __dataclass_params__: _DataclassParams


DataClassDecorator = Callable[[type], DataClass]


# main features
def dataarrayclass(
    cls: Optional[type] = None,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
) -> Union[DataClass, DataClassDecorator]:
    """Convert class to a DataArray class."""

    set_options = dataclass(
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
    )

    def to_dataclass(cls: type) -> DataClass:
        set_fields(cls)
        set_options(cls)
        return cls

    if cls is not None:
        return to_dataclass(cls)  # DataClass
    else:
        return to_dataclass  # DataClassDecorator


def asdataarray(obj: DataClass) -> xr.DataArray:
    """Convert dataclass instance to a DataArray instance."""
    fields = obj.__dataclass_fields__
    dataarray = fields["data"].type(obj.data)

    for field in fields.values():
        value = getattr(obj, field.name)
        set_value(dataarray, field, value)

    return dataarray


# helper features
def set_value(dataarray: xr.DataArray, field: Field, value: Any) -> xr.DataArray:
    """Set value to a DataArray instance according to given field."""
    kind = field.metadata["xarray"].kind

    if kind == Kind.ATTR:
        dataarray.attrs[field.name] = value
    elif kind == Kind.COORD:
        try:
            coord = field.type(value)
        except ValueError:
            shape = tuple(dataarray.sizes[dim] for dim in field.type.dims)
            coord = field.type(np.full(shape, value))
        finally:
            dataarray.coords[field.name] = coord
    elif kind == Kind.DATA:
        pass
    elif kind == Kind.NAME:
        dataarray.name = value

    return dataarray
