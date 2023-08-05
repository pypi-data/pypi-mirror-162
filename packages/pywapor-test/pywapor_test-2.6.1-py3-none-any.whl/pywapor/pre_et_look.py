"""
Generates input data for `pywapor.et_look`.
"""
from pywapor.collect import downloader
from pywapor.general.logger import log, adjust_logger
from pywapor.general import compositer
import pywapor.general.levels as levels
import datetime
import numpy as np
import os
import pandas as pd
import xarray as xr
from functools import partial
import pywapor.general.pre_defaults as defaults
from pywapor.general.variables import fill_attrs
from pywapor.enhancers.temperature import lapse_rate as _lapse_rate

def rename_vars(ds, *args):
    varis = ["p", "ra", "t_air", "t_air_min", "t_air_max", 
            "u2m", "v2m", "qv", "p_air", "p_air_0", "wv"]
    present_vars = [x for x in varis if x in ds.variables]
    ds = ds.rename({k: k + "_24" for k in present_vars})
    return ds

def lapse_rate(ds, *args):
    present_vars = [x for x in ds.variables if "t_air" in x]
    for var in present_vars:
        ds = _lapse_rate(ds, var)
    return ds

def calc_doys(ds, *args, bins = None):
    bin_doys = [int(pd.Timestamp(x).strftime("%j")) for x in bins]
    doy = np.mean([bin_doys[:-1], bin_doys[1:]], axis=0, dtype = int)
    if "time_bins" in list(ds.variables):
        ds["doy"] = xr.DataArray(doy, coords = ds["time_bins"].coords).chunk("auto")
    return ds

def add_constants(ds, *args):
    ds = ds.assign(defaults.constants_defaults())
    return ds

def main(folder, latlim, lonlim, timelim, sources = "level_1", bin_length = "DEKAD", 
            enhancers = [lapse_rate], diagnostics = None, example_source = None):
    """Prepare input data for `et_look`.

    Parameters
    ----------
    folder : str
        Path to folder in which to store (intermediate) data.
    latlim : list
        Latitude limits of area of interest.
    lonlim : list
        Longitude limits of area of interest.
    timelim : list
        Period for which to prepare data.
    sources : str | dict
        Configuration for each variable and source.
    bin_length : int | "DEKAD"
        Composite length.
    enhancers : list, optional
        Functions to apply to the xr.Dataset before creating the final
        output, by default "default".
    diagnostics : dict, optional
        Dictionary with coordinates and point-labels for which graphs can be 
        created.
    example_source : tuple, optional
        Which source to use for spatial alignment, overrides product selected
        through sources, by default None.

    Returns
    -------
    xr.Dataset
        Dataset with data for `pywapor.et_look`.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    _ = adjust_logger(True, folder, "INFO")

    t1 = datetime.datetime.now()
    log.info("> PRE_ET_LOOK").add()

    if isinstance(timelim[0], str):
        timelim[0] = datetime.datetime.strptime(timelim[0], "%Y-%m-%d")
        timelim[1] = datetime.datetime.strptime(timelim[1], "%Y-%m-%d")

    if isinstance(sources, str):
        sources = levels.pre_et_look_levels(sources)

    if isinstance(example_source, type(None)):
        example_source = levels.find_example(sources)
        log.info(f"--> Example dataset is {example_source[0]}.{example_source[1]}.")

    bins = compositer.time_bins(timelim, bin_length)

    enhancers = enhancers + [rename_vars, fill_attrs, partial(calc_doys, bins = bins),
                                add_constants]

    dss = downloader.collect_sources(folder, sources, latlim, lonlim, [bins[0], bins[-1]])

    if diagnostics:
        t_1 = datetime.datetime.now()
        log.info("> DIAGNOSTICS").add()
        ds = compositer.main(dss, sources, example_source, bins, folder, enhancers, diagnostics = diagnostics)
        t_2 = datetime.datetime.now()
        log.sub().info(f"< DIAGNOSTICS ({str(t_2 - t_1)})")
    else:
        ds = compositer.main(dss, sources, example_source, bins, folder, enhancers, diagnostics = None)

    t2 = datetime.datetime.now()
    log.sub().info(f"< PRE_ET_LOOK ({str(t2 - t1)})")

    return ds

if __name__ == "__main__":

    enhancers = "default"
    diagnostics = None
    example_source = None

#     import pywapor

#     folder = r"/Users/hmcoerver/pywapor_notebooks_b"
#     latlim = [28.9, 29.7]
#     lonlim = [30.2, 31.2]
#     timelim = ["2021-07-01", "2021-07-11"]
#     composite_length = "DEKAD"

#     et_look_version = "v2"
#     export_vars = "default"

#     level = "level_1"

#     et_look_sources = pywapor.general.levels.pre_et_look_levels(level)

#     et_look_sources = {k: v for k, v in et_look_sources.items() if k in ["ndvi", "z"]}

    # et_look_sources["ndvi"]["products"] = [
    #     {'source': 'MODIS',
    #         'product_name': 'MOD13Q1.061',
    #         'enhancers': 'default'},
    #     {'source': 'MODIS', 
    #         'product_name': 'MYD13Q1.061', 
    #         'enhancers': 'default'},
    #     {'source': 'PROBAV',
    #         'product_name': 'S5_TOC_100_m_C1',
    #         'enhancers': 'default',
    #         'is_example': True}
    # ]

    # et_look_sources["r0"]["products"] = [
    #     {'source': 'MODIS',
    #         'product_name': 'MCD43A3.061',
    #         'enhancers': 'default'},
    #     {'source': 'PROBAV',
    #         'product_name': 'S5_TOC_100_m_C1',
    #         'enhancers': 'default'}
    # ]

    # se_root_sources = pywapor.general.levels.pre_se_root_levels(level)
    # se_root_sources["ndvi"]["products"] = et_look_sources["ndvi"]["products"]

    # from functools import partial
    # et_look_sources["se_root"]["products"] = [
    #     {'source': partial(pywapor.se_root.se_root, sources = se_root_sources),
    #         'product_name': 'v2',
    #         'enhancers': 'default'},]

    # ds = pywapor.pre_et_look.main(folder, latlim, lonlim, timelim, 
    #                                 sources = et_look_sources,
    #                                 bin_length = composite_length)



