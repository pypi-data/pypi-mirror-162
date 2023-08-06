import logging
import re
import time
import traceback
from pathlib import Path

import click
import dask.array as da
import xarray as xr
from aicspylibczi import CziFile
from distributed import LocalCluster

from .array import cziArray

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


__version__ = "0.2.3"
__author__ = "Eduardo Gonzalez Solares"
__email__ = "E.GonzalezSolares@ast.cam.ac.uk"


EXPR = [r"[\(_ -](\d+)\)?.czi", r"[\(_ -](\d+)\)?(\S+)?.czi", r"(\d+).czi"]


def _parse_section(filename):
    fname = filename.name if isinstance(filename, Path) else filename
    for expr in EXPR:
        match = re.search(expr, fname)
        if match:
            s = match.groups()[0]
            break
    s = int(s)
    return f"S{s:03d}"


def _get_coords(czi_files: list[Path]):
    x_shape = 1
    y_shape = 1
    m_shape = 1
    c_shape = 1
    s_shape = 1
    for this_file in czi_files:
        czi = CziFile(this_file)
        shape = czi.get_dims_shape()[0]
        x_shape = shape["X"][1] if shape["X"][1] > x_shape else x_shape
        y_shape = shape["Y"][1] if shape["Y"][1] > y_shape else y_shape
        m_shape = shape["M"][1] if shape["M"][1] > m_shape else m_shape
        c_shape = shape["C"][1] if shape["C"][1] > c_shape else c_shape
        s_shape = shape["S"][1] if shape["S"][1] > s_shape else s_shape

    coords = {
        "z": range(s_shape),
        "channel": range(c_shape),
        "tile": range(m_shape),
        "y": range(y_shape),
        "x": range(x_shape),
    }

    return coords


def convert2zarr(input_path: Path, output_path: Path):
    logger.info("Processing %s", input_path)
    czi_files = [*input_path.glob("*.czi")]
    czi_files.sort(key=_parse_section)

    coords = _get_coords(czi_files)
    logger.info(f"Coords: {coords}")

    # Initialize storage
    ds = xr.Dataset(coords=coords)
    ds.to_zarr(output_path, mode="w")

    attrs = {"orig_name": input_path.name}

    for this_file in czi_files:
        watch = time.monotonic()
        czi = CziFile(this_file)
        czif = cziArray(czi)
        if -1 in czif.shape:
            logger.error("Skipping %s - invalid size", this_file.name)
            continue

        section_name = _parse_section(this_file.name)

        shape = tuple(max(val) + 1 for val in coords.values())
        arr = da.zeros(shape, chunks=(1, 1, 1, shape[-2], shape[-1]))
        arrz = xr.DataArray(arr, coords=coords, attrs=czif.metadata, name=section_name)
        ds = xr.Dataset(coords=coords)
        ds[section_name] = arrz
        ds = ds.astype("uint16")
        ds.to_zarr(output_path, mode="a")

        arr = da.from_array(czif, chunks=czif.chunks)
        arrx = xr.DataArray(
            arr, coords=czif.dimensions, attrs=czif.metadata, name=section_name
        )
        ds = xr.Dataset(coords=czif.dimensions)
        ds[section_name] = arrx
        ds = ds.astype("uint16")
        ds.attrs = attrs
        nz, nch, nt, ny, nx = arr.shape
        ds.to_zarr(
            output_path,
            mode="a",
            region={
                "z": slice(0, nz),
                "channel": slice(0, nch),
                "tile": slice(0, nt),
                "y": slice(0, ny),
                "x": slice(0, nx),
            },
        )
        logger.info(
            "Processed section %s - %s (%s)",
            section_name,
            this_file.name,
            time.monotonic() - watch,
        )

        del czi, czif, arr, arrx, ds


def axio2zarr(input_path, output_path):
    input_fn = Path(input_path)
    output_fn = Path(output_path) / input_fn.name
    with LocalCluster(processes=False, dashboard_address=None):
        convert2zarr(input_fn, output_fn)
    return f"{output_fn}"


@click.command()
@click.argument("input_path")
@click.argument("output_path")
def main(input_path, output_path):
    try:
        axio2zarr(input_path, output_path)
    except Exception as err:
        print(f"Error: {str(err)}")
        print(f"Details: {traceback.format_exc()}")
