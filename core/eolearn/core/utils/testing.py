"""
The eodata module provides core objects for handling remote sensing multi-temporal data (such as satellite imagery).

Copyright (c) 2017- Sinergise and contributors
For the full list of contributors, see the CREDITS file in the root directory of this source tree.

This source code is licensed under the MIT license, see the LICENSE file in the root directory of this source tree.
"""
import datetime as dt
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas.testing import assert_geodataframe_equal
from numpy.testing import assert_array_equal

from sentinelhub import CRS, BBox

from ..constants import FeatureType
from ..eodata import EOPatch
from ..utils.parsing import FeatureParser

DEFAULT_BBOX = BBox((0, 0, 100, 100), crs=CRS("EPSG:32633"))


@dataclass
class PatchGeneratorConfig:
    """Dataclass containing a more complex setup of the PatchGenerator class."""

    num_timestamps: int = 5
    timestamps_range: Tuple[dt.datetime, dt.datetime] = (dt.datetime(2019, 1, 1), dt.datetime(2019, 12, 31))
    timestamps: List[dt.datetime] = field(init=False, repr=False)

    max_integer_value: int = 256
    raster_shape: Tuple[int, int] = (98, 151)
    depth_range: Tuple[int, int] = (1, 3)

    def __post_init__(self) -> None:
        self.timestamps = list(pd.date_range(*self.timestamps_range, periods=self.num_timestamps).to_pydatetime())


def generate_eopatch(
    features: Optional[List[Tuple[FeatureType, str]]] = None,
    bbox: BBox = DEFAULT_BBOX,
    timestamps: Optional[List[dt.datetime]] = None,
    seed: int = 42,
    config: Optional[PatchGeneratorConfig] = None,
) -> EOPatch:
    """A class for generating EOPatches with dummy data."""
    config = config if config is not None else PatchGeneratorConfig()
    supported_feature_types = [ftype for ftype in FeatureType if ftype.is_array()]
    parsed_features = FeatureParser(features or [], supported_feature_types).get_features()
    rng = np.random.default_rng(seed)

    timestamps = timestamps if timestamps is not None else config.timestamps
    patch = EOPatch(bbox=bbox, timestamps=timestamps)

    # fill eopatch with random data
    # note: the patch generation functionality could be extended by generating extra random features
    for ftype, fname in parsed_features:
        shape = _get_feature_shape(rng, ftype, timestamps, config)
        patch[(ftype, fname)] = _generate_feature_data(rng, ftype, shape, config)
    return patch


def _generate_feature_data(
    rng: np.random.Generator, ftype: FeatureType, shape: Tuple[int, ...], config: PatchGeneratorConfig
) -> np.ndarray:
    if ftype.is_discrete():
        return rng.integers(config.max_integer_value, size=shape)
    return rng.normal(size=shape)


def _get_feature_shape(
    rng: np.random.Generator, ftype: FeatureType, timestamps: List[dt.datetime], config: PatchGeneratorConfig
) -> Tuple[int, ...]:
    time, height, width, depth = len(timestamps), *config.raster_shape, rng.integers(*config.depth_range)

    if ftype.is_spatial() and not ftype.is_vector():
        return (time, height, width, depth) if ftype.is_temporal() else (height, width, depth)
    return (time, depth) if ftype.is_temporal() else (depth,)


def assert_feature_data_equal(tested_feature: Any, expected_feature: Any) -> None:
    """Asserts that the data of two features is equal. Cases are specialized for common data found in EOPatches."""
    if isinstance(tested_feature, np.ndarray) and isinstance(expected_feature, np.ndarray):
        assert_array_equal(tested_feature, expected_feature)
    elif isinstance(tested_feature, gpd.GeoDataFrame) and isinstance(expected_feature, gpd.GeoDataFrame):
        assert CRS(tested_feature.crs) == CRS(expected_feature.crs)
        assert_geodataframe_equal(
            tested_feature, expected_feature, check_crs=False, check_index_type=False, check_dtype=False
        )
    else:
        assert tested_feature == expected_feature
