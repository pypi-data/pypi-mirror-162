#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""CCD detector modeling class."""

import typing as t

from pyxel.detectors import Detector

if t.TYPE_CHECKING:
    import pandas as pd

    from pyxel.detectors import CCDCharacteristics, CCDGeometry, Environment


class CCD(Detector):
    """Charge-Coupled Device class containing all detector attributes and data."""

    def __init__(
        self,
        geometry: "CCDGeometry",
        environment: "Environment",
        characteristics: "CCDCharacteristics",
    ):
        self._geometry = geometry  # type: CCDGeometry
        self._characteristics = characteristics  # type: CCDCharacteristics

        super().__init__(environment=environment)
        super().reset()

    def __eq__(self, other) -> bool:
        return (
            type(self) == type(other)
            and self.geometry == other.geometry
            and self.environment == other.environment
            and self.characteristics == other.characteristics
            and super().__eq__(other)
        )

    @property
    def geometry(self) -> "CCDGeometry":
        """TBW."""
        return self._geometry

    @property
    def characteristics(self) -> "CCDCharacteristics":
        """TBW."""
        return self._characteristics

    # TODO: Refactor this
    def to_dict(self) -> t.Mapping:
        """Convert an instance of `CCD` to a `dict`."""
        dct = {
            "version": 1,
            "type": "CCD",
            "properties": {
                "geometry": self.geometry.to_dict(),
                "environment": self.environment.to_dict(),
                "characteristics": self.characteristics.to_dict(),
            },
            "data": {
                "photon": None if self._photon is None else self._photon.array.copy(),
                "pixel": None if self._pixel is None else self._pixel.array.copy(),
                "signal": None if self._signal is None else self._signal.array.copy(),
                "image": None if self._image is None else self._image.array.copy(),
                "charge": None
                if self._charge is None
                else {
                    "array": self._charge.array.copy(),
                    "frame": self._charge.frame.copy(),
                },
            },
        }

        return dct

    # TODO: Refactor this
    @classmethod
    def from_dict(cls, dct: t.Mapping) -> "CCD":
        """Create a new instance of `CCD` from a `dict`."""
        # TODO: This is a simplistic implementation. Improve this.
        from pyxel.detectors import CCDCharacteristics, CCDGeometry, Environment

        if dct["type"] != "CCD":
            raise ValueError

        if dct["version"] != 1:
            raise ValueError

        properties = dct["properties"]
        geometry = CCDGeometry.from_dict(properties["geometry"])
        environment = Environment.from_dict(properties["environment"])
        characteristics = CCDCharacteristics.from_dict(properties["characteristics"])

        detector = cls(
            geometry=geometry,
            environment=environment,
            characteristics=characteristics,
        )

        data = dct["data"]

        if "photon" in data:
            detector.photon.array = data["photon"]
        if "pixel" in data:
            detector.pixel.array = data["pixel"]
        if "signal" in data:
            detector.signal.array = data["signal"]
        if "image" in data:
            detector.image.array = data["image"]
        if "charge" in data and data["charge"] is not None:
            charge_dct = data["charge"]
            detector.charge._array = charge_dct["array"]

            new_frame = charge_dct["frame"]  # type: pd.DataFrame
            previous_frame = detector.charge._frame  # type: pd.DataFrame
            detector.charge._frame = new_frame[previous_frame.columns]

        return detector
