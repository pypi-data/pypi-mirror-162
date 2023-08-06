# -*- coding: utf-8 -*-
# ____________________________________________________________________________________________________________________ #
#                                                                                                                      #
#          888888888888                                         88                                                     #
#               88                                              ""                                                     #
#               88                                                                                                     #
#               88   ,adPPYba,  8b,dPPYba,  88,dPYba,,adPYba,   88  8b,dPPYba,   88       88  ,adPPYba,                #
#               88  a8P_____88  88P'   "Y8  88P'   "88"    "8a  88  88P'   `"8a  88       88  I8[    ""                #
#               88  8PP"""""""  88          88      88      88  88  88       88  88       88   `"Y8ba,                 #
#               88  "8b,   ,aa  88          88      88      88  88  88       88  "8a,   ,a88  aa    ]8I                #
#               88   `"Ybbd8"'  88          88      88      88  88  88       88   `"YbbdP'Y8  `"YbbdP"'                #
#
# -------------------------------------------------------------------------------------------------------------------- #
import re
import os
import json
from datetime import datetime
import numpy as N

from pymses import RamsesOutput
from pymses.analysis import cube3d, ScalarOperator, Camera
from pymses.utils import constants as C


def _convert_data_ref_to_ramses_ioutput_endianness(ramses_output_ref):
    """
    Convert the output reference (directory name or number) to the (integer) output number + endianness flag (opt.)

    Parameters
    ----------
    data_ref: ramses output data reference

    Returns
    -------
    iout: Ramses output number
    """
    if isinstance(ramses_output_ref, basestring):
        m = re.match("^(output_)?0*(?P<iout>[0-9]+)(;(?P<endianness>(NAT|BIG|LIT)))?$",
                     ramses_output_ref)
        if m is not None:
            d = m.groupdict()
            iout = int(d.get('iout', "-1"))
            if iout > -1:
                if d['endianness'] == "BIG":
                    endian = ">"
                elif d["endianness"] == "LIT":
                    endian = "<"
                else:  # 'NAT' or None
                    endian = '='
                return iout, endian

        raise IOError("Cannot determine (output number, endianness) with the data reference "
                      "'{dref!s}'".format(dref=ramses_output_ref))

    else:  # Integer value
        iout = int(ramses_output_ref)
        return iout, '='


def _convert_center_coord_to_box_size_unit(coord_data, ramses_out_length_unit):
    """
    Convert datacube center coordinate data into a Ramses boxsize unit float value.

    Parameters
    ----------
    coord_data: `float` or [`float`, `str`] `list`
        coordinate data to convert

    Returns
    -------
    coord: `float`
        converted coordinate value in boxsize unit
    """
    if isinstance(coord_data, list):
        if len(coord_data) < 2:
            raise AttributeError(
                "Datacube center coordinate \"{cd!s}\" is not in a valid format".format(cd=str(coord_data)))
        val = coord_data[0]
        unit_name = str(coord_data[1])
        try:
            unit = C.Unit.from_name(unit_name)
        except AttributeError:
            raise AttributeError("Invalid datacube center coordinate unit '{u!s}'".format(u=unit_name))
        coord = val * unit.express(ramses_out_length_unit)
    else:
        coord = float(coord_data)
    return coord


def temp_func(dset):
    P = dset["P"]
    rho = dset["rho"]
    temp = N.zeros_like(P)
    dense_cells = rho > 0.0
    temp[dense_cells] = P[dense_cells] / rho[dense_cells]
    temp[~dense_cells] = N.max(temp)
    return temp


def run(data_path, data_ref, field='gas density', xcenter=0.5, ycenter=0.5, zcenter=0.5, size=0.1, nres=128,
        out_format="FITS"):
    """
    Sample a scalar quantity define on a 3D AMR Ramses grid over a cartesian 3D datacube

    Parameters
    ----------
    data_path: base data directory path
    data_ref: Ramses output reference
    field: scalar quantity reference. Available choices are :
        * 'gas density' (default)
        * 'gas temperature'
        * 'gas velocity along x axis'
        * 'gas velocity along y axis'
        * 'gas velocity along z axis'
        * 'magnetic field along x axis'
        * 'magnetic field along y axis'
        * 'magnetic field along z axis'
    xcenter: datacube center x-axis coordinate. Default 0.5
    ycenter: datacube center y-axis coordinate. Default 0.5
    zcenter: datacube center z-axis coordinate. Default 0.5
    size: datacube size. Default 0.1
    nres: datacube resolution (default 128^3)
    out_format: data output format ("FITS" or "HDF5"). Default "FITS"
    """
    # Start time
    str_beg = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if out_format not in ["HDF5", "FITS"]:
        raise AttributeError("Invalid output format (valid values are 'FITS' and 'HDF5').")

    # Get Ramses output
    iout, endianness = _convert_data_ref_to_ramses_ioutput_endianness(data_ref)
    ro = RamsesOutput(data_path, iout, order=endianness)  # , verbose=False)
    ul = ro.info["unit_length"]

    # Define AMR scalar fields
    ro.define_amr_scalar_field("hydro", "rho", 0)
    ro.define_amr_vector_field("hydro", "vel", [1, 2, 3])
    ro.define_amr_vector_field("hydro", "Bl", [4, 5, 6])
    ro.define_amr_vector_field("hydro", "Br", [7, 8, 9])
    ro.define_amr_scalar_field("hydro", "P", 10)

    # Setup camera
    xc = _convert_center_coord_to_box_size_unit(xcenter, ul)
    yc = _convert_center_coord_to_box_size_unit(ycenter, ul)
    zc = _convert_center_coord_to_box_size_unit(zcenter, ul)
    cam = Camera(center=[xc, yc, zc])  # , region_size=[size, size], distance=size / 2., far_cut_depth=size / 2.,
    #                  map_max_size=nres)

    field_list = []
    if field == 'gas density':
        field_list.append('rho')
    elif field == 'gas temperature':
        field_list.append('rho')
        field_list.append("P")
    elif re.match("^gas\svelocity\salong\s(x|y|z)\saxis$", field) is not None:
        field_list.append("vel")
    elif re.match("^magnetic\sfield\salong\s(x|y|z)\saxis$", field) is not None:
        field_list.append("Bl")
        field_list.append("Br")
    amr_source = ro.amr_source(field_list)

    # Setup the scalar operator based on the user-defined scalar field name
    if field == 'gas density':
        uf = ro.info["unit_density"].express(C.H_cc)
        op = ScalarOperator(lambda dset: dset["rho"] * uf, C.H_cc)
    elif field == 'gas temperature':
        uf = ro.info["unit_temperature"].express(C.K)
        op = ScalarOperator(lambda dset: temp_func(dset) * uf, C.K)
    elif field == "gas velocity along x axis":
        uf = ro.info["unit_velocity"].express(C.km_s)
        op = ScalarOperator(lambda dset: dset["vel"][..., 0] * uf, C.km_s)
    elif field == "gas velocity along y axis":
        uf = ro.info["unit_velocity"].express(C.km_s)
        op = ScalarOperator(lambda dset: dset["vel"][..., 1] * uf, C.km_s)
    elif field == "gas velocity along z axis":
        uf = ro.info["unit_velocity"].express(C.km_s)
        op = ScalarOperator(lambda dset: dset["vel"][..., 2] * uf, C.km_s)
    elif field == "magnetic field along x axis":
        uf = ro.info["unit_mag"].express(C.mGauss)
        op = ScalarOperator(lambda dset: (dset["Br"][..., 0] + dset["Bl"][..., 0])*uf / 2.0, C.mGauss)
    elif field == "magnetic field along y axis":
        uf = ro.info["unit_mag"].express(C.mGauss)
        op = ScalarOperator(lambda dset: (dset["Br"][..., 1] + dset["Bl"][..., 1])*uf / 2.0, C.mGauss)
    elif field == "magnetic field along z axis":
        uf = ro.info["unit_mag"].express(C.mGauss)
        op = ScalarOperator(lambda dset: (dset["Br"][..., 2] + dset["Bl"][..., 2])*uf / 2.0, C.mGauss)
    else:
        # Unknown field => raise attribute error
        raise AttributeError("Invalid scalar quantity '{f!s}'.".format(f=field))

    # Create CubeExtractor data processor instance and build datacube
    p = cube3d.CubeExtractor(amr_source, op)
    # p.disable_multiprocessing()
    cube_data = p.process(cam, cube_size=size, resolution=nres)

    # Save FITS/HDF5 in out/ directory
    if out_format == "HDF5":
        cube_data.save_HDF5(os.path.join('out', 'datacube.h5'))
        result_dict = {'HDF5': 'datacube.h5'}
    else:  # Default => save to FITS file
        cube_data.save_fits(os.path.join('out', 'datacube.fits'), axis_unit=None)  # Use camera size unit
        result_dict = {'FITS': 'datacube.fits'}

    # Stop time
    str_fin = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # --------------------------- Save run info in JSON config file (documentation) ---------------------------------- #
    # Get simulation data path relative to base data directory (in 'TERMINUS_DATA_DIR' env. variable)
    base_job_dir = os.environ.get("TERMINUS_DATA_DIR", None)
    if base_job_dir is not None:
        job_dir_relative_data_path = data_path.replace(os.path.join(base_job_dir, ''), '')
    else:
        job_dir_relative_data_path = data_path

    d = {'service_name': 'datacube_3d_mhd',
         'host': os.environ.get("TERMINUS_HOSTNAME", 'unknown'),
         'data': {'data_path': job_dir_relative_data_path, 'data_reference': data_ref},
         'run_parameters': {'xcenter': xcenter, 'ycenter': ycenter, 'zcenter': zcenter,
                            'field': field, 'size': size, 'nres': nres},
         'time_info': {'job_start': str_beg, 'job_finished': str_fin},
         'results': result_dict
         }
    with open(os.path.join("out", "processing_config.json"), 'w') as f:
        json.dump(d, f, indent=4)
    # ---------------------------------------------------------------------------------------------------------------- #


__all__ = ["run"]
