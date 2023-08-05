"""Plotting utilities.
"""
from astropy.units import degree

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import healpy as hp
from datetime import timedelta

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames

from astropy.time import Time

from km3net_testdata import data_path

import km3astro.coord as kc
import km3astro.frame as kf
import km3astro.toolbox as kt
import tempfile
import os


def ra_dec(skycoord):
    """Take (ra, dec) from skycoord in matplotlib-firendly format.

    This wraps the ra because astropy's convention differs from matplotlib.
    """
    ra = skycoord.ra.wrap_at(180 * degree).radian
    dec = skycoord.dec.radian
    return ra, dec


def projection_axes(projection="aitoff", **figargs):
    fig = plt.figure(**figargs)
    ax = fig.add_subplot(111, projection=projection)
    ax.grid(color="lightgrey")
    return ax


def plot_equatorial(
    evts,
    projection="aitoff",
    ax=None,
    marker="o",
    markersize=4,
    alpha=0.8,
    adjust_subplots=True,
    **kwargs
):
    ra, dec = ra_dec(evts)
    if ax is None:
        ax = projection_axes(projection=projection)
    ax.plot(ra, dec, marker, markersize=markersize, alpha=alpha, **kwargs)
    if adjust_subplots:
        plt.subplots_adjust(top=0.95, bottom=0.0)
    return ax


def get_coord_from_skycoord(SC, frame, detector):
    """Return the coordinate of a SkyCoord object for aitoff or mollweide projection

    Parameters
    ----------
    SC : astropy.SkyCoord
        The sky coordinate.
    frame : str
        The frame of the coordinate, either "ParticleFrame" or "UTM" or "altaz" or "equatorial" or "galactic"
    detector : str [default = "antares"]
        Detector of the coordinate, either "orca", "arca" or "antares".

    Returns
    -------
    (phi, theta)/(az, ze)/(alt, az)/(ra, dec)/(l, b) : (float, float)
        The set of coordinate.

    """
    SC_copy = kc.transform_to(SC, frame, detector)

    if frame == "ParticleFrame":
        phi = SC_copy.phi.wrap_at(180 * u.deg).radian

        theta = SC_copy.theta.radian

        if type(theta) == np.float64:
            if theta > np.pi / 2:
                theta = theta - np.pi

        if type(theta) == np.ndarray:
            print(len(theta))
            for idx, t in enumerate(theta):
                if t > np.pi / 2:
                    theta[idx] = t - np.pi

        return phi, theta

    elif frame == "UTM":
        az = SC_copy.azimuth.wrap_at(180 * u.deg).radian
        ze = SC_copy.alt_utm.radian
        return az, ze

    elif frame == "altaz":
        alt = SC_copy.alt.radian
        az = SC_copy.az.wrap_at(180 * u.deg).radian
        return alt, az

    elif frame == "equatorial":
        ra = SC_copy.ra.wrap_at(180 * u.deg).radian
        dec = SC_copy.dec.radian
        return ra, dec

    elif frame == "galactic":
        l = SC_copy.l.wrap_at(180 * u.deg).radian
        b = SC_copy.b.radian
        return l, b

    else:
        raise ValueError("Error: Wrong Frame input frame")
        return None


def plot_SkyCoord(
    SC,
    frame,
    detector,
    projection="aitoff",
    ax=None,
    marker="s",
    markersize=3,
    alpha=0.8,
    adjust_subplots=True,
    **kwargs
):
    """Plot given SkyCoord object or list"""

    Coord_lon, Coord_lat = get_coord_from_skycoord(SC, frame, detector)

    if ax is None:
        ax = projection_axes(projection=projection)
    ax.plot(Coord_lon, Coord_lat, marker, markersize=markersize, alpha=alpha, **kwargs)
    if adjust_subplots:
        plt.subplots_adjust(top=0.95, bottom=0.0)
    return ax


def get_Sky_label(SC, frame, detector, time=False):
    """Return the coordinate of a SkyCoord object as string to use as label for matplotlib.

    Parameters
    ----------
    SC : astropy.SkyCoord
        The sky coordinate.
    frame : str
        The frame of the coordinate, either "ParticleFrame" or "UTM" or "altaz" or "equatorial" or "galactic"
    detector : str [default = "antares"]
        Detector of the coordinate, either "orca", "arca" or "antares".
    time : bool
        Bool to integrate or no the time in the label.

    Returns
    -------
    labels : str
        A string containing the coordinate and time if asked to use as label.

    """

    a, b = get_coord_from_skycoord(SC, frame, detector)
    a = a * 180 / np.pi
    a = float("{:.2f}".format(a))
    b = b * 180 / np.pi
    b = float("{:.2f}".format(b))

    labels = ""

    xlab = ""
    ylab = ""
    timelab = ""

    if time == True:
        timelab = str(SC.obstime)

    if frame == "ParticleFrame":
        xlab = "Phi = " + str(a)
        ylab = " Theta = " + str(b) + " [deg]"

    elif frame == "UTM":
        xlab = "Azimuth = " + str(a)
        ylab = " Zenith = " + str(b) + " [deg]"

    elif frame == "equatorial":
        xlab = "RA = " + str(a)
        ylab = " DEC = " + str(b) + " [deg] (ICRS)"

    elif frame == "galactic":
        xlab = "l = " + str(a)
        ylab = " b = " + str(b) + " [deg]"

    else:
        raise ValueError("Error: Wrong Frame input frame")
        return None

    labels = xlab + ylab + " " + timelab
    return labels


def get_label(plot_frame):
    """Return the Axis label corresponding to the plot frame.

    Parameters
    ----------
    plot_frame : str
        The plot frame.

    Returns
    -------
    (xlab, ylab) : (str,str)
        X and Y axis name to use as label.

    """

    if plot_frame == "ParticleFrame":
        xlab = "Phi / deg"
        ylab = "Theta / deg"
        return xlab, ylab

    elif plot_frame == "UTM":
        xlab = "Azimuth / deg"
        ylab = "Zenith / deg"
        return xlab, ylab

    elif plot_frame == "equatorial":
        xlab = "RA(ICRS) /deg"
        ylab = "DEC(ICRS) / deg"
        return xlab, ylab

    elif plot_frame == "galactic":
        xlab = "Gal_lon /deg"
        ylab = "Gal_lat /deg"
        return xlab, ylab

    else:
        raise ValueError("Error: Wrong Frame input frame")
        return None


def get_horizon(detector, time, frame, alt_cut=5.7):
    """Calculate the Horizon line of view for a given detector, time and frame system.

    Parameters
    ----------
    detector : str
        Detector to use, either "orca", "arca" or "antares".

    time : str or astropy.Time
        The time of observation of the alert.

    frame : str
        The frame to return the calculated horizon, either "ParticleFrame" or "UTM" or "equatorial" or "galactic"
    cut : float[default = 5.7]
        Value in degree of the cut in Altitude for Altaz frame. By default at 5.7 degree corresponding to cos(0.1).

    Returns
    -------
    horizon : np.ndarray(astropy.SkyCoord)
        A list of SkyCoord representing the horizon line of view.

    """

    n = 360
    alts = alt_cut * np.ones(n)
    azs = np.zeros(n)

    for i in range(n):
        azs[i] = i

    obstime = Time(time)
    loc = kf.get_location(detector)

    horizon = SkyCoord(
        alt=alts * u.degree,
        az=azs * u.degree,
        obstime=obstime,
        location=loc,
        frame="altaz",
    )

    horizon = kc.transform_to(horizon, frame, detector)

    return horizon


def get_galactic_plan(detector, time, frame):
    """Calculate the Galactic plan for a given detector, time and frame system.

    Parameters
    ----------
    detector : str
        Detector to use, either "orca", "arca" or "antares".

    time : str or astropy.Time
        The time of observation of the alert.

    frame : str
        The frame to return the calculated horizon, either "ParticleFrame" or "UTM" or "equatorial" or "galactic"

    Returns
    -------
    gal_plan : np.ndarray(astropy.SkyCoord)
        A list of SkyCoord representing the galactic plan.

    """
    n = 360
    l = np.zeros(n)
    b = np.zeros(n)

    for i in range(n):
        l[i] = i

    obstime = Time(time)
    loc = kf.get_location(detector)

    gal_plan = SkyCoord(
        l=l * u.degree, b=b * u.degree, obstime=obstime, location=loc, frame="galactic"
    )

    gal_plan = kc.transform_to(gal_plan, frame, detector)

    return gal_plan


def get_obstime(table_Sky, it=0):
    """return the observation time for a table of SkyCoord at given index."""
    return table_Sky.iloc[it]["SkyCoord_base"].obstime


def plot_pd_skycoord(table_skycoord, plot_frame, detector_to, projection, ax):
    """plot a pandas DataFrame of SkyCoord."""
    table_skycoord.apply(
        lambda x: plot_SkyCoord(
            x.SkyCoord_base,
            frame=plot_frame,
            detector=detector_to,
            projection=projection,
            markersize=10,
            marker=".",
            color="royalblue",
            ax=ax,
            label=get_Sky_label(x.SkyCoord_base, plot_frame, detector_to),
        ),
        axis=1,
    )


def plot_file(file0, ax, projection, frame, detector, plot_frame, detector_to):
    """plot a csv file containing alerts."""
    table_read = pd.read_csv(file0, comment="#")
    table_skycoord = kt.build_skycoord_list(table_read, frame, detector)
    plot_pd_skycoord(table_skycoord, plot_frame, detector_to, projection, ax)


def calculate_visibility_map(detector="orca", frame="equatorial", alt_cut=5.7):
    """Calculate the visibility map of a detector in a frame for a given cut on altitude.
       Warning: Time of Calcultation can be really long.

    Parameters
    ----------

    detector : str [default=orca]
        The detector to use for calculation, either "orca", "arca" or "antares.
    frame : str [default="equatorial"]
        The frame to use for the visibility map, either "equatorial" or "galactic"
    alt_cut : float [default=5.7]
        The cut in altitude of the detector line of view. default is 5.7 degree corresponding to cos(0.1)

    Returns
    -------

    visi_map : csv
        Write a file containing the visibility map table.
        Already included visibility_map: antares, orca, arca in equatorial and galactic

    """

    Ntime = 24
    day = 24

    visi_map = np.zeros((360, 180))
    counter = 0
    print(len(visi_map))
    print(len(visi_map[0]))
    for i in range(len(visi_map)):

        for j in range(len(visi_map[i])):
            counter += 1
            print(str(counter) + "/" + str(len(visi_map) * len(visi_map[0])))
            prob = 0
            for k in range(Ntime):

                sec = 24 * 60 * 60 / Ntime
                dtime = timedelta(seconds=sec * k)
                date = "2022-01-01"
                time = str(dtime)

                SC = kt.global_transform(
                    frame, "altaz", date, time, i, (j - 90), "deg", detector
                )
                if SC.alt.deg < alt_cut:
                    prob += 1
            print("Prob = " + str(prob))
            prob = prob / Ntime
            visi_map[i][j] = prob

    path = "skymap_plot/"
    name = "visibility_map_" + frame + "_" + detector + ".csv"

    pd.DataFrame(visi_map).to_csv(path + name, index=None, header=None)


def read_visibility_map(visi_map):
    """Read a given visibility map"""

    data = pd.read_csv(visi_map, sep=",", header=None)
    return data


def get_visi_map_path(frame, detector):
    """Return the path to a visibility map for a given frame and detector"""
    path = (
        os.path.dirname(os.path.abspath(__file__))
        + "/data/visibility_map_"
        + frame
        + "_"
        + detector
        + ".csv"
    )
    return path


def plot_visibility(ax, frame="equatorial", detector="antares"):
    """Plot on the background the visibility map corresponding to the frame and detector"""
    visi_map = get_visi_map_path(frame, detector)

    visi_data = read_visibility_map(visi_map).to_numpy()

    x = np.arange(-90, 90, 1)
    y = np.arange(-180, 180, 1)
    x = x * (2 * np.pi / 360)
    y = y * (2 * np.pi / 360)

    pc = ax.pcolormesh(y, x, visi_data.T, alpha=1, cmap="Greys_r", shading="gouraud")
    plt.colorbar(pc, shrink=0.6)


def skymap_hpx(file0, path="", name=""):
    # to be updated for GW healpix url
    """Method to plot a skymap from an hpx url

    Parameters
    ----------
    file0 : str
    The path to the healpix file.
    path : str
        Path to the writing location.
    name : str
        Path and name of where to write the skymap png file.

    Returns:
    Fig : file.png
       A png file of the skymap.
    """

    projection = "mollweide"
    ax = projection_axes(projection=projection, figsize=[40 / 2.54, 30 / 2.54])

    gw_map = hp.read_map(file0)
    hp.mollview(
        gw_map,
    )
    hp.graticule()

    if path != "":
        if name == "":
            name = path + "hpx_skymap_maker_test.png"
        else:
            name = path + name

    else:
        path = tempfile.TemporaryDirectory()

        if name == "":
            name = "hpx_skymap_maker_test.png"

    plt.savefig(name)


def skymap_list(
    file0="",
    frame="equatorial",
    detector="antares",
    plot_frame="equatorial",
    detector_to="antares",
    path="",
    name="",
):
    """Method to plot a skymap from a list of alert in a csv file.

    Parameters
    ----------
    file0 : str
        The path to the csv file containing the list of alert.
    frame :str [default = "equatorial"]
        The frame of alerts in file0
    detector : str [default = "antares"]
        The detector of the alerts, either "orca", "arca" or "antares"
    plot_frame : str [default = "equatorial"]
        The frame of the skymap, either "equatorial" or "galactic"
    detector_to :str [default = "antares"]
        The detector to use for frame transformation, either "orca", "arca" or "antares"
    path : str
        Path to the writing location
    name : str
        Name the skymap png file.

    Returns:
    Fig : file.png
       A png file of the skymap.
    """

    if file0 == "":
        file0 = data_path("astro/antares_coordinate_systems_benchmark.csv")

    projection = "aitoff"
    ax = projection_axes(projection=projection, figsize=[40 / 2.54, 30 / 2.54])

    table_read = pd.read_csv(file0, comment="#")
    table_skycoord = kt.build_skycoord_list(table_read, frame, detector)

    plot_file(file0, ax, projection, frame, detector, plot_frame, detector_to)
    plot_visibility(ax=ax, frame=plot_frame, detector=detector_to)

    title = detector + " Alert List " + plot_frame + " frame skymap"
    ax.set_title(title, fontsize=20, y=1.1)
    xlabel, ylabel = get_label(plot_frame)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if path != "":
        if name == "":
            name = path + "skymap_list_" + detector + "_test_" + plot_frame + ".png"
        else:
            name = path + name
    else:
        path = tempfile.TemporaryDirectory()

        if name == "":
            name = "skymap_list_" + detector + "_test_" + plot_frame + ".png"

    plt.savefig(name)


def skymap_alert(
    file0="",
    ra=1000,
    dec=1000,
    obstime="",
    frame="equatorial",
    detector="antares",
    plot_frame="equatorial",
    detector_to="antares",
    alt_cut=5.7,
    path="",
    name="",
):
    """Method to plot a skymap from an alert in a csv file or by giving RA, DEC and obstime.

    Parameters
    ----------
    file0 : str [default = ""]
        The path to the csv file containing the alert.
    ra, dec : (float,float)
        The ra and dec coordinate of the alert.
    obstime : str
        The observation time of the alert. Format is "YYYY-MM-DDTHH:MM:SS"
    frame :str [default = "equatorial"]
        The frame of the alert.
    detector : str [default = "antares"]
        The detector of the alert.
    plot_frame : str [default = "equatorial"]
        The frame of the skymap, either "ParticleFrame", "UTM", "equatorial" or "galactic"
    detector_to :str [default = "antares"]
        The detector to use for frame transformation, either "orca", "arca" or "antares"
    alt_cut : float [default = 5.7]
        The altitude cut on detector visibility for horizon calculation. default is alt_cut = 5.7 degree which correspond to cos(0.1).
    path : str
        Path to the writing location.
    name : str [default = ""]
        Name of the skymap png file.

    Returns:
    Fig : file.png
       A png file of the skymap.
    """

    use_coord = False
    use_file = False

    if file0 != "":
        use_file = True

    if ra != 1000 or dec != 1000 or obstime != "":
        use_coord = True

    if use_coord == False and use_file == False:
        file0 = data_path("astro/antares_moon_sun_position_benchmark.csv")
        ra = 80
        dec = 15
        obstime = "2022-06-15T03:03:03"
        use_coord = True
        use_file = True

    projection = "aitoff"
    ax = projection_axes(projection=projection, figsize=[40 / 2.54, 30 / 2.54])

    if use_file == True:

        table_read = pd.read_csv(file0, comment="#")
        table_skycoord = kt.build_skycoord_list(table_read, frame, detector)
        obstime = get_obstime(table_skycoord)
        plot_file(file0, ax, projection, frame, detector, plot_frame, detector_to)

    if use_coord == True:

        alert = SkyCoord(
            ra=ra * u.degree, dec=dec * u.degree, obstime=obstime, frame="icrs"
        )

        plot_SkyCoord(
            alert,
            frame=plot_frame,
            detector=detector_to,
            projection=projection,
            ax=ax,
            marker=".",
            markersize=10,
            linewidth=0,
            color="royalblue",
            label=get_Sky_label(alert, plot_frame, detector_to, time=False),
        )

    horizon = get_horizon(
        detector=detector_to, time=obstime, frame=plot_frame, alt_cut=alt_cut
    )

    plot_SkyCoord(
        horizon,
        frame=plot_frame,
        detector=detector_to,
        projection=projection,
        ax=ax,
        marker=".",
        markersize=10,
        linewidth=0,
        color="lime",
    )

    gal_plan = get_galactic_plan(detector=detector_to, time=obstime, frame=plot_frame)
    plot_SkyCoord(
        gal_plan,
        frame=plot_frame,
        detector=detector_to,
        projection=projection,
        ax=ax,
        marker=".",
        markersize=10,
        linewidth=0,
        color="red",
    )

    date, time = str(obstime).split("T", 1)

    title = detector + " Alert " + plot_frame + " frame skymap " + date + " " + time
    ax.set_title(title, fontsize=20, y=1.1)
    xlabel, ylabel = get_label(plot_frame)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    horizon_line = mlines.Line2D(
        [], [], color="lime", marker=".", markersize=1, label="Horizon"
    )
    gal_line = mlines.Line2D(
        [], [], color="red", marker=".", markersize=1, label="Galactic plan"
    )

    h, l = ax.get_legend_handles_labels()
    h.append(horizon_line)
    h.append(gal_line)

    plt.legend(handles=h, bbox_to_anchor=(1.05, 1.05))

    if path != "":
        if name == "":
            name = path + "skymap_alert_" + detector + "_test_" + plot_frame + ".png"
        else:
            name = path + name

    else:
        path = tempfile.TemporaryDirectory()
        if name == "":
            name = "skymap_alert_" + detector + "_test_" + plot_frame + ".png"

    plt.savefig(name)
