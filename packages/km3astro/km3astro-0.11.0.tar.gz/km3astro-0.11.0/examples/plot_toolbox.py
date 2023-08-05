"""
========================
Multiple exemple of how to use km3astro.toolbox
========================

"""

# Author: Tedjditi Hichem <htedjditi@km3net.de>

import km3astro.toolbox as ktb
from km3net_testdata import data_path


def main():

    ##########################################################
    # Alert Coordinates
    # --------------------
    # Let's define one event.

    det = "antares"
    date = "2007-10-04"
    time = "03:03:03"
    phi = 97.07
    theta = 135.0
    az = 277.07
    ze = 45.00
    ra = 70.613
    dec = -1.852
    l = 198.7
    b = -29.298

    ##########################################################
    # Let's do some transformation with toolbox.function

    print("Starting test of toolbox")
    print()
    print("TESTING PRINT EQ TO XXX")

    ktb.print_eq_to_utm(ra, dec, date, time, det)
    ktb.print_eq_to_loc(ra, dec, date, time, det)
    ktb.print_eq_to_gal(ra, dec, date, time)
    print()
    print("TESTING PRINT LOC TO XXX")

    ktb.print_loc_to_eq(phi, theta, date, time, det)
    ktb.print_loc_to_utm(phi, theta, date, time, det)
    ktb.print_loc_to_gal(phi, theta, date, time, det)
    print()
    print("TESTING TRANSFORM FILE")

    ##########################################################
    # Let's transform a file with a list of alert
    # --------------------
    ##########################################################
    # Let's take one list of event.

    file0 = data_path("astro/antares_astro_objects_benchmark.csv")

    ##########################################################
    # Let's define the frame of the alert and the frame to transform to.

    frame_from = "ParticleFrame"
    frame_to = "equatorial"

    ktb.transform_file(
        file0,
        frame_from,
        frame_to,
        detector_from="antares",
        detector_to="antares",
        name="test_toolbox.csv",
    )


if __name__ == "__main__":
    main()
