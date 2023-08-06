#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import typing as t
from collections import abc
from pathlib import Path

import h5py as h5
import numpy as np
import pandas as pd

from pyxel import __version__

ATTRIBUTES = {
    "photon": {"name": "Photon", "unit": "photon/s"},
    "charge": {"name": "Charge", "unit": "electron"},
    "pixel": {"name": "Pixel", "unit": "electron"},
    "signal": {"name": "Signal", "unit": "volt"},
    "image": {"name": "Image", "unit": "adu"},
}  # type: t.Mapping[str, t.Mapping[str, str]]


def _store(
    h5file: h5.File,
    name: str,
    dct: t.Mapping[str, t.Union[int, float, pd.DataFrame, pd.Series, np.ndarray, dict]],
    attributes: t.Optional[t.Mapping[str, t.Mapping[str, str]]] = None,
) -> None:
    """Write data into a new HDF5 group.

    Parameters
    ----------
    h5file : h5.File
        Writeable HDF5 file object.
    name : str
        Name of the HDF5 group to create. (e.g. '/' or '/geometry')
    dct : dict
        Data to write into a HDF5 dataset.
    attributes : dict
        Attributes to store.
    """
    for key, value in dct.items():
        new_name = f"{name}/{key}"

        if isinstance(value, (int, float)) or value is None:
            if value is None:
                value = np.nan

            dataset = h5file.create_dataset(
                name=new_name, data=value, shape=()
            )  # type: h5.Dataset

            if attributes is not None and key in attributes:
                dataset.attrs.update(attributes[key])

        elif isinstance(value, pd.DataFrame):
            new_group = h5file.create_group(name=new_name)  # type: h5.Group
            new_group.attrs["type"] = "DataFrame"

            _store(h5file, name=new_name, dct=value.to_dict(orient="series"))

        elif isinstance(value, (pd.Series, np.ndarray, abc.Sequence)):
            dataset = h5file.create_dataset(name=new_name, data=np.asarray(value))

            if attributes is not None and key in attributes:
                dataset.attrs.update(attributes[key])

        elif isinstance(value, dict):
            new_group = h5file.create_group(name=new_name)

            if attributes is not None and key in attributes:
                new_group.attrs.update(attributes[key])

            _store(h5file, name=new_name, dct=value)

        else:
            raise NotImplementedError


def to_hdf5(filename: t.Union[str, Path], dct: t.Mapping[str, t.Any]) -> None:
    """Write data to a HDF5 file."""
    if dct["version"] != 1:
        raise NotImplementedError

    with h5.File(filename, mode="w") as h5file:
        # Write main attributes
        h5file.attrs["version"] = dct["version"]
        h5file.attrs["type"] = dct["type"]
        h5file.attrs["pyxel-version"] = str(__version__)

        _store(h5file, name="/geometry", dct=dct["properties"]["geometry"])
        _store(h5file, name="/environment", dct=dct["properties"]["environment"])
        _store(
            h5file, name="/characteristics", dct=dct["properties"]["characteristics"]
        )

        _store(h5file, name="/data", dct=dct["data"], attributes=ATTRIBUTES)


def _load(
    h5file: h5.File, name: str
) -> t.Union[None, int, float, t.Mapping[str, t.Any], np.ndarray, pd.DataFrame]:
    """Write data from a HDF5 group.

    Parameters
    ----------
    h5file : h5.File
        Readable HDF5 file object.
    name : str
        Name of the HDF5 group to read. (e.g. '/' or '/geometry')

    Returns
    -------
    dict
        Data to read from a HDF5 dataset.
    """
    dataset = h5file[name]  # type: t.Union[h5.Dataset, h5.Group]

    if isinstance(dataset, h5.Group):
        dct = {}
        for key, _ in h5file[name].items():
            result = _load(h5file, name=f"{name}/{key}")

            dct[key] = result

        if name.endswith("frame"):
            return pd.DataFrame.from_dict(dct)
        else:
            return dct

    elif isinstance(dataset, h5.Dataset):
        if dataset.ndim == 0:
            value = np.array(dataset)

            if np.isnan(value):
                return None
            elif np.issubdtype(dataset.dtype, np.integer):
                return int(value)
            elif np.issubdtype(dataset.dtype, np.floating):
                return float(value)
            else:
                raise TypeError
        else:
            return np.array(dataset)
    else:
        raise NotImplementedError


def from_hdf5(filename: t.Union[str, Path]) -> t.Mapping[str, t.Any]:
    """Read data from a HDF5 file."""
    dct = {}
    with h5.File(filename, mode="r") as h5file:
        # Read main attributes
        dct.update(h5file.attrs)

        # TODO: Use a JSON schema to validate 'dct'
        if "version" not in dct or "type" not in dct:
            raise ValueError("Missing 'version' and/or 'type' !")

        version = dct["version"]  # type: int
        if version != 1:
            raise NotImplementedError

        # Get properties
        properties = {}
        for name in ["geometry", "environment", "characteristics"]:  # type: str
            properties[name] = _load(h5file, name=f"/{name}")

        dct["properties"] = properties

        # Get data
        data = {}
        for name in h5file["/data"]:
            data[name] = _load(h5file, name=f"/data/{name}")

        dct["data"] = data

    return dct
