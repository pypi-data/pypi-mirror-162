# -*- coding: utf-8 -*-
from pymses import RamsesOutput
from pymses.analysis import splatting, raytracing, ScalarOperator, Camera
from pymses.utils import constants as C
import os
import re
import numpy as N


class MapGasDensityProcessor(object):
    """
    Gas surface density processor
    """
    _outdir_regexp = re.compile("output_[0-9]{5}")
    _iout_regexp = re.compile("[0-9]{5}")

    def __init__(self, ramses_dir, ioutput):
        super(MapGasDensityProcessor, self).__init__()
        self._ramses_output_dir = ramses_dir
        self._ramses_iout = ioutput

    def do(self, cam, use_raytracing=True):
        # Get Ramses data
        ro = RamsesOutput(self._ramses_output_dir, self._ramses_iout)#, verbose=False)
        amr = ro.amr_source(["rho"])

        if not use_raytracing:
            # Map operator : gas surface density map
            scal_func = ScalarOperator(lambda dset: dset["rho"] * dset.get_sizes() ** 3,
                                       ro.info["unit_density"] * ro.info["unit_length"])

            # Map processing
            mp = splatting.SplatterProcessor(amr, ro.info, scal_func)
            # mp.disable_multiprocessing()

            dmap = mp.process(cam)
        else:
            # Map operator : gas surface density map
            scal_func = ScalarOperator(lambda dset: dset["rho"], ro.info["unit_density"]*ro.info["unit_length"])

            # Map processing
            rt = raytracing.RayTracer(amr, ro.info, scal_func)
            # rt.disable_multiprocessing()

            dmap = rt.process(cam)

        return dmap


def run(data_path, data_ref, xcenter=0.5, ycenter=0.5, zcenter=0.5, los_axis='z', size=1.0):
    """

    :param data_path:
    :param data_ref:
    :param xcenter:
    :param ycenter:
    :param zcenter:
    :param los_axis:
    :param size:
    :return:
    """
    iout = int(data_ref)
    item_index = 534
    p = MapGasDensityProcessor(data_path, iout)

    center = [xcenter, ycenter, zcenter]
    mwidth = size
    mheight = size
    mdepth = size
    msize = 512

    cam = Camera(center=center, line_of_sight_axis=los_axis, up_vector='x', region_size=[mwidth, mheight], distance=mdepth/2., far_cut_depth=mdepth/2., map_max_size=msize)

    datamap = p.do(cam, use_raytracing=True)
    datamap.save_HDF5("out/gas_clump_%s_%d.h5" % (los_axis, item_index))
    datamap.save_PNG(img_fname="out/gas_clump_%s_%d.png" % (los_axis, item_index), cmap='BlackBlueWhiteRed')


__all__ = ["run"]
