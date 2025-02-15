"""
This module implements feature types used in EOPatch objects

Copyright (c) 2017- Sinergise and contributors
For the full list of contributors, see the CREDITS file in the root directory of this source tree.

This source code is licensed under the MIT license, see the LICENSE file in the root directory of this source tree.
"""
import warnings
from enum import Enum, EnumMeta
from typing import Any, Optional

from sentinelhub import BBox, MimeType
from sentinelhub.exceptions import deprecated_function

from .exceptions import EODeprecationWarning

TIMESTAMP_COLUMN = "TIMESTAMP"


def _warn_and_adjust(name: str) -> str:
    # since we stick with `UPPER` for attributes and `lower` for values, we include both to reuse function
    deprecation_msg = None
    if name in ("TIMESTAMP", "timestamp"):
        name = "TIMESTAMPS" if name == "TIMESTAMP" else "timestamps"

    if deprecation_msg:
        warnings.warn(deprecation_msg, category=EODeprecationWarning, stacklevel=3)  # type: ignore
    return name


class EnumWithDeprecations(EnumMeta):
    """A custom EnumMeta class for catching the deprecated Enum members of the FeatureType Enum class."""

    def __getattribute__(cls, name: str) -> Any:
        return super().__getattribute__(_warn_and_adjust(name))

    def __getitem__(cls, name: str) -> Any:
        return super().__getitem__(_warn_and_adjust(name))

    def __call__(cls, value: str, *args: Any, **kwargs: Any) -> Any:
        return super().__call__(_warn_and_adjust(value), *args, **kwargs)


class FeatureType(Enum, metaclass=EnumWithDeprecations):
    """The Enum class of all possible feature types that can be included in EOPatch.

    List of feature types:
     - DATA with shape t x n x m x d: time- and position-dependent remote sensing data (e.g. bands) of type float
     - MASK with shape t x n x m x d: time- and position-dependent mask (e.g. ground truth, cloud/shadow mask,
       super pixel identifier) of type int
     - SCALAR with shape t x s: time-dependent and position-independent remote sensing data (e.g. weather data,) of
       type float
     - LABEL with shape t x s: time-dependent and position-independent label (e.g. ground truth) of type int
     - VECTOR: a list of time-dependent vector shapes in shapely.geometry classes
     - DATA_TIMELESS with shape n x m x d: time-independent and position-dependent remote sensing data (e.g.
       elevation model) of type float
     - MASK_TIMELESS with shape n x m x d: time-independent and position-dependent mask (e.g. ground truth,
       region of interest mask) of type int
     - SCALAR_TIMELESS with shape s:  time-independent and position-independent remote sensing data of type float
     - LABEL_TIMELESS with shape s: time-independent and position-independent label of type int
     - VECTOR_TIMELESS: time-independent vector shapes in shapely.geometry classes
     - META_INFO: dictionary of additional info (e.g. resolution, time difference)
     - BBOX: bounding box of the patch which is an instance of sentinelhub.BBox
     - TIMESTAMPS: list of dates which are instances of datetime.datetime
    """

    # IMPORTANT: these feature names must exactly match those in EOPatch constructor
    DATA = "data"
    MASK = "mask"
    SCALAR = "scalar"
    LABEL = "label"
    VECTOR = "vector"
    DATA_TIMELESS = "data_timeless"
    MASK_TIMELESS = "mask_timeless"
    SCALAR_TIMELESS = "scalar_timeless"
    LABEL_TIMELESS = "label_timeless"
    VECTOR_TIMELESS = "vector_timeless"
    META_INFO = "meta_info"
    BBOX = "bbox"
    TIMESTAMPS = "timestamps"

    @classmethod
    def has_value(cls, value: str) -> bool:
        """True if value is in FeatureType values. False otherwise."""
        return value in cls._value2member_map_

    def is_spatial(self) -> bool:
        """True if FeatureType has a spatial component. False otherwise."""
        return self in [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.VECTOR,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.VECTOR_TIMELESS,
        ]

    def is_temporal(self) -> bool:
        """True if FeatureType has a time component. False otherwise."""
        return self in [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.VECTOR,
            FeatureType.TIMESTAMPS,
        ]

    def is_timeless(self) -> bool:
        """True if FeatureType doesn't have a time component and is not a meta feature. False otherwise."""
        return not (self.is_temporal() or self.is_meta())

    def is_discrete(self) -> bool:
        """True if FeatureType should have discrete (integer) values. False otherwise."""
        return self in [FeatureType.MASK, FeatureType.MASK_TIMELESS, FeatureType.LABEL, FeatureType.LABEL_TIMELESS]

    def is_meta(self) -> bool:
        """True if FeatureType is for storing metadata info and False otherwise."""
        return self in [FeatureType.META_INFO, FeatureType.BBOX, FeatureType.TIMESTAMPS]

    def is_vector(self) -> bool:
        """True if FeatureType is vector feature type. False otherwise."""
        return self in [FeatureType.VECTOR, FeatureType.VECTOR_TIMELESS]

    def is_array(self) -> bool:
        """True if FeatureType stores a dictionary with array data. False otherwise."""
        return self in [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.SCALAR_TIMELESS,
            FeatureType.LABEL_TIMELESS,
        ]

    def is_image(self) -> bool:
        """True if FeatureType stores a dictionary with arrays that represent images. False otherwise."""
        return self.is_array() and self.is_spatial()

    @deprecated_function(
        EODeprecationWarning, "Use the equivalent `is_array` method, or consider if `is_image` fits better."
    )
    def is_raster(self) -> bool:
        """True if FeatureType stores a dictionary with raster data. False otherwise."""
        return self.is_array()

    @deprecated_function(EODeprecationWarning)
    def has_dict(self) -> bool:
        """True if FeatureType stores a dictionary. False otherwise."""
        return self in [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.VECTOR,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.SCALAR_TIMELESS,
            FeatureType.LABEL_TIMELESS,
            FeatureType.VECTOR_TIMELESS,
            FeatureType.META_INFO,
        ]

    @deprecated_function(EODeprecationWarning)
    def contains_ndarrays(self) -> bool:
        """True if FeatureType stores a dictionary of numpy.ndarrays. False otherwise."""
        return self.is_array()

    def ndim(self) -> Optional[int]:
        """If given FeatureType stores a dictionary of numpy.ndarrays it returns dimensions of such arrays."""
        if self.is_array():
            return {
                FeatureType.DATA: 4,
                FeatureType.MASK: 4,
                FeatureType.SCALAR: 2,
                FeatureType.LABEL: 2,
                FeatureType.DATA_TIMELESS: 3,
                FeatureType.MASK_TIMELESS: 3,
                FeatureType.SCALAR_TIMELESS: 1,
                FeatureType.LABEL_TIMELESS: 1,
            }[self]
        return None

    @deprecated_function(EODeprecationWarning)
    def type(self) -> type:
        """Returns type of the data for the given FeatureType."""
        if self is FeatureType.TIMESTAMPS:
            return list
        if self is FeatureType.BBOX:
            return BBox
        return dict

    @deprecated_function(EODeprecationWarning)
    def file_format(self) -> MimeType:
        """Returns a mime type enum of a file format into which data of the feature type will be serialized"""
        if self.is_array():
            return MimeType.NPY
        if self.is_vector():
            return MimeType.GPKG
        if self is FeatureType.BBOX:
            return MimeType.GEOJSON
        return MimeType.JSON


class DeprecatedCollectionClass(type):
    """A custom meta class for raising a warning when collections of the deprecated FeatureTypeSet class are used."""

    def __getattribute__(cls, name: str) -> Any:
        if not name.startswith("_"):
            warnings.warn(
                (
                    "The `FeatureTypeSet` collections are deprecated. The argument `allowed_feature_types` of feature"
                    " parsers can now be a callable, so you can use `lambda ftype: ftype.is_spatial()` instead of"
                    " `FeatureTypeSet.SPATIAL_TYPES` in such cases."
                ),
                category=EODeprecationWarning,
                stacklevel=3,
            )
        return super().__getattribute__(name)


class FeatureTypeSet(metaclass=DeprecatedCollectionClass):
    """A collection of immutable sets of feature types, grouped together by certain properties."""

    SPATIAL_TYPES = frozenset(
        [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.VECTOR,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.VECTOR_TIMELESS,
        ]
    )
    TEMPORAL_TYPES = frozenset(
        [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.VECTOR,
            FeatureType.TIMESTAMPS,
        ]
    )
    TIMELESS_TYPES = frozenset(
        [
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.SCALAR_TIMELESS,
            FeatureType.LABEL_TIMELESS,
            FeatureType.VECTOR_TIMELESS,
        ]
    )
    DISCRETE_TYPES = frozenset(
        [FeatureType.MASK, FeatureType.MASK_TIMELESS, FeatureType.LABEL, FeatureType.LABEL_TIMELESS]
    )
    META_TYPES = frozenset([FeatureType.META_INFO, FeatureType.BBOX, FeatureType.TIMESTAMPS])
    VECTOR_TYPES = frozenset([FeatureType.VECTOR, FeatureType.VECTOR_TIMELESS])
    RASTER_TYPES = frozenset(
        [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.SCALAR_TIMELESS,
            FeatureType.LABEL_TIMELESS,
        ]
    )
    DICT_TYPES = frozenset(
        [
            FeatureType.DATA,
            FeatureType.MASK,
            FeatureType.SCALAR,
            FeatureType.LABEL,
            FeatureType.VECTOR,
            FeatureType.DATA_TIMELESS,
            FeatureType.MASK_TIMELESS,
            FeatureType.SCALAR_TIMELESS,
            FeatureType.LABEL_TIMELESS,
            FeatureType.VECTOR_TIMELESS,
            FeatureType.META_INFO,
        ]
    )
    RASTER_TYPES_4D = frozenset([FeatureType.DATA, FeatureType.MASK])
    RASTER_TYPES_3D = frozenset([FeatureType.DATA_TIMELESS, FeatureType.MASK_TIMELESS])
    RASTER_TYPES_2D = frozenset([FeatureType.SCALAR, FeatureType.LABEL])
    RASTER_TYPES_1D = frozenset([FeatureType.SCALAR_TIMELESS, FeatureType.LABEL_TIMELESS])


class OverwritePermission(Enum):
    """Enum class which specifies which content of saved EOPatch can be overwritten when saving new content.

    Permissions are in the following hierarchy:

    - `ADD_ONLY` - Only new features can be added, anything that is already saved cannot be changed.
    - `OVERWRITE_FEATURES` - Overwrite only data for features which have to be saved. The remaining content of saved
      EOPatch will stay unchanged.
    - `OVERWRITE_PATCH` - Overwrite entire content of saved EOPatch and replace it with the new content.
    """

    ADD_ONLY = 0
    OVERWRITE_FEATURES = 1
    OVERWRITE_PATCH = 2
