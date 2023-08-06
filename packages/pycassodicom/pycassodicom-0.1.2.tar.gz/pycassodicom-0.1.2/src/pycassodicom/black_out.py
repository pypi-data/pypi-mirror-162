"""
PycassoDicom

Script for de-identifying images with burned in annotation.
Depending on manufacturer and image size, pixel can be blackened.
Some images are of no use for the researcher or have too much identifying information.
They will be deleted (set to None).
"""
from typing import Optional

import numpy as np
from pydicom import Dataset
from pydicom.uid import ExplicitVRLittleEndian


def blacken_pixels(ds: Dataset) -> Dataset:
    """
    Blacken pixel based on manufacturer, modality and image size.
    """
    try:
        if (ds.Modality == 'CT') \
                and (ds.Manufacturer == 'Agfa') \
                and (ds.Rows == 775) \
                and (ds.Columns == 1024):
            img = ds.pixel_array
            img[0:round(img.shape[0] * 0.07), :] = 0  # ca. 7%

            ds.PixelData = img.tobytes()
            ds.PhotometricInterpretation = 'YBR_FULL'                   # important!!
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian     # because changed
            return ds

        if ds.ManufacturerModelName == 'iE33' and ds.Rows == 600 and ds.Columns == 800:
            img = ds.pixel_array
            img = np.repeat(img[:, :, :, 0, np.newaxis], 3, axis=3)
            img[:, 0:round(img.shape[1] * 0.1), :, :] = 0

            ds.PixelData = img
            ds.PhotometricInterpretation = 'RGB'                        # important!!
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian     # because changed

            return ds

        if ds.ManufacturerModelName == 'iE33' and ds.Rows == 768 and ds.Columns == 1024:
            img = ds.pixel_array
            img[0:round(img.shape[0] * 0.1), :, :] = 0

            ds.PixelData = img
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian     # because changed

            return ds

    except AttributeError:
        return ds

    return ds


def delete_dicom(ds: Dataset) -> Optional[Dataset]:
    """
    Return None if the dicom can be deleted.
    """
    try:
        if (ds.Modality == 'CT') \
                and (ds.Manufacturer == 'SIEMENS') \
                and (ds.ImageType[:4] == ['DERIVED', 'SECONDARY', 'OTHER', 'VPCT']) \
                and (ds.Rows == 968) \
                and (ds.Columns == 968):
            return None

        if (ds.ManufacturerModelName == 'iE33') and (ds.ImageType == ['ORIGINAL', 'PRIMARY', 'INVALID']):
            return None

    except AttributeError:
        return ds

    return ds
