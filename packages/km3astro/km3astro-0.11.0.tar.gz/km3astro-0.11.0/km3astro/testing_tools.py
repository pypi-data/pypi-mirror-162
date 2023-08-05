""" km3astro.testing_tools for tests/test_benchmark.py"""

import numpy as np
import pandas as pd

import km3astro.coord as kc
import km3astro.toolbox as ktb


def test_Skycoord_separation(SC_true, SC_check):
    """Calculate the angle separation between two SkyCoord object

    Parameters
    ----------
    SC_true : astropy.SkyCoord
        Sky coordinate of reference
    SC_check : astropy.SkyCoord
        Sky coordinate to be checked

    Returns
    -------
    sep_deg : float
        The angle between the two Sky coordinate object
    """

    sep = SC_true.separation(SC_check)
    sep_deg = sep.deg
    return sep_deg


def test_benchmark_conversion(table_true, table_check):
    """Calculate the angle separation between two pandas DataFrame of SkyCoord object

    Parameters
    ----------
    table_true : pandas.DataFrame(astropy.SkyCoord)
        Pandas DataFrame of the Sky coordinate of reference
    table_check : pandas.DataFrame(astropy.SkyCoord)
        Pandas DataFrame of the Sky coordinate to be checked

    Returns
    -------
    sep_table : pandas.DataFrame(float)
        DataFrame of the angle between the two table of Sky coordinate object
    """

    data = [table_true["SkyCoord_base"], table_check["SkyCoord_new"]]
    table = pd.concat(data, axis=1)

    sep_table = table.apply(
        lambda x: test_Skycoord_separation(x.SkyCoord_base, x.SkyCoord_new),
        axis=1,
        result_type="expand",
    )

    return sep_table


def test_angle_separation(file0, detector="antares", detector_to="antares"):
    """Test the angle separation of between a benchmark table and km3astro.coord transformation tool.
    for test purpose only.

    Parameters
    ----------
    file0 : str
        path to the benchmark table.
    detector : str [default = "antares"]
        Detector of the benchmark table, either "orca", "arca" or "antares"
    detector_to : str [default = "antares"]
        Detector of the new frame, either "orca", "arca" or "antares"

    """
    table_read = ktb.reader_from_file(file0)

    angle_treshold = 0.02

    if set(["phi", "theta"]).issubset(table_read.columns):

        table_loc_to_utm = kc.transform_to_new_frame(
            table_read, "ParticleFrame", "UTM", detector, detector_to
        )
        table_loc_to_eq = kc.transform_to_new_frame(
            table_read, "ParticleFrame", "equatorial", detector, detector_to
        )
        table_loc_to_gal = kc.transform_to_new_frame(
            table_read, "ParticleFrame", "galactic", detector, detector_to
        )

    if set(["azimuth", "zenith"]).issubset(table_read.columns):

        table_utm_to_loc = kc.transform_to_new_frame(
            table_read, "UTM", "ParticleFrame", detector, detector_to
        )
        table_utm_to_eq = kc.transform_to_new_frame(
            table_read, "UTM", "equatorial", detector, detector_to
        )
        table_utm_to_gal = kc.transform_to_new_frame(
            table_read, "UTM", "galactic", detector, detector_to
        )

    if set(["RA-J2000", "DEC-J2000"]).issubset(table_read.columns):

        table_eq_to_utm = kc.transform_to_new_frame(
            table_read, "equatorial", "UTM", detector, detector_to
        )
        table_eq_to_loc = kc.transform_to_new_frame(
            table_read, "equatorial", "ParticleFrame", detector, detector_to
        )
        table_eq_to_gal = kc.transform_to_new_frame(
            table_read, "equatorial", "galactic", detector, detector_to
        )

    if set(["gal_lon", "gal_lat"]).issubset(table_read.columns):

        table_gal_to_loc = kc.transform_to_new_frame(
            table_read, "galactic", "ParticleFrame", detector, detector_to
        )
        table_gal_to_eq = kc.transform_to_new_frame(
            table_read, "galactic", "equatorial", detector, detector_to
        )
        table_gal_to_utm = kc.transform_to_new_frame(
            table_read, "galactic", "UTM", detector, detector_to
        )

    # testing angle separation
    if set(["phi", "theta"]).issubset(table_read.columns):

        if set(["azimuth", "zenith"]).issubset(table_read.columns):
            sep_utm_to_loc = test_benchmark_conversion(
                table_loc_to_utm, table_utm_to_loc
            )

            mean_ = sep_utm_to_loc.mean()
            min_ = sep_utm_to_loc.min()
            max_ = sep_utm_to_loc.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["RA-J2000", "DEC-J2000"]).issubset(table_read.columns):
            sep_eq_to_loc = test_benchmark_conversion(table_loc_to_eq, table_eq_to_loc)

            mean_ = sep_eq_to_loc.mean()
            min_ = sep_eq_to_loc.min()
            max_ = sep_eq_to_loc.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["gal_lon", "gal_lat"]).issubset(table_read.columns):

            sep_gal_to_loc = test_benchmark_conversion(
                table_loc_to_gal, table_gal_to_loc
            )

            mean_ = sep_gal_to_loc.mean()
            min_ = sep_gal_to_loc.min()
            max_ = sep_gal_to_loc.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

    if set(["azimuth", "zenith"]).issubset(table_read.columns):

        if set(["phi", "theta"]).issubset(table_read.columns):
            sep_loc_to_utm = test_benchmark_conversion(
                table_utm_to_loc, table_loc_to_utm
            )

            mean_ = sep_loc_to_utm.mean()
            min_ = sep_loc_to_utm.min()
            max_ = sep_loc_to_utm.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["RA-J2000", "DEC-J2000"]).issubset(table_read.columns):
            sep_eq_to_utm = test_benchmark_conversion(table_utm_to_eq, table_eq_to_utm)

            mean_ = sep_eq_to_utm.mean()
            min_ = sep_eq_to_utm.min()
            max_ = sep_eq_to_utm.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["gal_lon", "gal_lat"]).issubset(table_read.columns):
            sep_gal_to_utm = test_benchmark_conversion(
                table_utm_to_gal, table_gal_to_utm
            )

            mean_ = sep_gal_to_utm.mean()
            min_ = sep_gal_to_utm.min()
            max_ = sep_gal_to_utm.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

    if set(["RA-J2000", "DEC-J2000"]).issubset(table_read.columns):

        if set(["phi", "theta"]).issubset(table_read.columns):
            sep_loc_to_eq = test_benchmark_conversion(table_eq_to_loc, table_loc_to_eq)

            mean_ = sep_loc_to_eq.mean()
            min_ = sep_loc_to_eq.min()
            max_ = sep_loc_to_eq.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["azimuth", "zenith"]).issubset(table_read.columns):
            sep_utm_to_eq = test_benchmark_conversion(table_eq_to_utm, table_utm_to_eq)

            mean_ = sep_utm_to_eq.mean()
            min_ = sep_utm_to_eq.min()
            max_ = sep_utm_to_eq.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["gal_lon", "gal_lat"]).issubset(table_read.columns):
            sep_gal_to_eq = test_benchmark_conversion(table_eq_to_gal, table_gal_to_eq)

            mean_ = sep_gal_to_eq.mean()
            min_ = sep_gal_to_eq.min()
            max_ = sep_gal_to_eq.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

    if set(["gal_lon", "gal_lat"]).issubset(table_read.columns):

        if set(["phi", "theta"]).issubset(table_read.columns):
            sep_loc_to_gal = test_benchmark_conversion(
                table_gal_to_loc, table_loc_to_gal
            )

            mean_ = sep_loc_to_gal.mean()
            min_ = sep_loc_to_gal.min()
            max_ = sep_loc_to_gal.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["azimuth", "zenith"]).issubset(table_read.columns):
            sep_utm_to_gal = test_benchmark_conversion(
                table_gal_to_utm, table_utm_to_gal
            )

            mean_ = sep_utm_to_gal.mean()
            min_ = sep_utm_to_gal.min()
            max_ = sep_utm_to_gal.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )

        if set(["RA-J2000", "DEC-J2000"]).issubset(table_read.columns):
            sep_eq_to_gal = test_benchmark_conversion(table_gal_to_eq, table_eq_to_gal)

            mean_ = sep_eq_to_gal.mean()
            min_ = sep_eq_to_gal.min()
            max_ = sep_eq_to_gal.max()

            if max_ > angle_treshold:
                raise AssertionError(
                    "Error: Maximum angle separation = "
                    + str(max_)
                    + " > "
                    + str(angle_treshold)
                )
