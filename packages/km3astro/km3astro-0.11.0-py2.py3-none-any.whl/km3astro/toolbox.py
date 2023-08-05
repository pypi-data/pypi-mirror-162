import numpy as np
import pandas as pd

import km3astro.coord as kc
import km3astro.frame as kf


def get_az_zenith(SC, detector="antares", unit="deg"):
    """Get the azimuth and zenith for a given sky coordinate

    Parameters
    ----------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    detector : str [default: "antares"]
    The name of the detector, either "antares", "orca" or "arca"
    unit : str
    The unit to be used on the output values, either "deg" or "rad"

    Returns
    -------
    (azimuth, zenith): (float, float)
    Azimuth and zenith in the requested unit
    """

    SC_copy = SC.copy()
    loc = kf.get_location(detector)

    if SC.frame.name != "utm":
        raise ValueError("Wrong Frame: Expected 'utm' but got " + SC.frame.name)

    zenith = SC_copy.zenith.rad
    az = SC_copy.azimuth.rad

    if unit == "deg":
        zenith = SC_copy.zenith.deg
        az = SC_copy.azimuth.deg

    return az, zenith


def get_phi_theta(SC, detector="antares", unit="deg"):
    """Get the phi and theta for a given sky coordinate

    Parameters
    ----------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    detector : str [default: "antares"]
    The name of the detector, either "antares", "orca" or "arca"
    unit : str
    The unit to be used on the output values, either "deg" or "rad"

    Returns
    -------
    (phi, theta): (float, float)
    phi and theta in the requested unit
    """

    SC_copy = SC.copy()
    loc = kf.get_location(detector)

    if SC.frame.name != "particleframe":
        raise ValueError(
            "Wrong Frame: Expected 'particleframe' but got " + SC.frame.name
        )

    phi = SC_copy.phi.rad
    theta = SC_copy.theta.rad

    if unit == "deg":
        phi = SC_copy.phi.deg
        theta = SC_copy.theta.deg

    return phi, theta


def get_alt_az(SC, unit="deg"):
    """Get the altitude and azimuth for a given sky coordinate

    Parameters
    ----------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    unit : str
        The unit to be used on the output values, either "deg" or "rad"

    Returns
    -------
    (altitude, azimuth): (float, float)
    altitude and azimuth in the requested unit
    """

    if SC.frame.name != "altaz":
        raise Exception("Wrong Frame: Expected altAz but got " + SC.frame.name)

    alt = SC.alt
    az = SC.az

    if unit == "deg":
        alt = SC.alt.deg
        az = SC.az.deg

    return alt, az


def get_ra_dec(SC, unit="deg"):
    """Get the right ascension and declination for a given sky coordinate

    Parameters
    ----------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    unit : str
    The unit to be used on the output values, either "deg" or "rad" or "hourangle"

    Returns
    -------
    (ra, dec): (float, float)
    Ra and dec in the requested unit
    """

    if SC.frame.name != "icrs" and SC.frame.name != "fk5":
        raise Exception("Wrong Frame: Expected icrs or fk5 but got " + SC.frame.name)

    ra = SC.ra
    dec = SC.dec

    if unit == "deg":
        ra = SC.ra.deg
        dec = SC.dec.deg

    if unit == "hourangle":
        ra = Angle(ra, unit="hourangle")
        ra = ra.to_string()
        dec = dec

    return ra, dec


def get_l_b(SC, unit="deg"):
    """Get the galactic longitude and galactic latiture for a given sky coordinate

    Parameters
    ----------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    unit : str
    The unit to be used on the output values, either "deg" or "rad"

    Returns
    -------
    (l, b): (float, float)
    l and b in the requested unit
    """

    if SC.frame.name != "galactic":
        raise ValueError("Wrong Frame: Expected galactic but got " + SC.frame.name)

    l = SC.l
    b = SC.b

    if unit == "deg":
        l = SC.l.deg
        b = SC.b.deg

    return l, b


def global_transform(frame_from, frame_to, *args):
    """Global frame transformation function

    Parameters
    ----------
    frame_from : str
        The frame of the input coordinate, either "ParticleFrame" or "UTM" or "equatorial" or "galactic"
    frame_to : str
        The desired frame of the output sky coordinate
    *args : list of the coordinate Parameters
        The sky coordinate parameters. Varies with frame_from and follow "km3astro.coord.build_event" function for reference.

    Returns
    -------
    sky_object: astropy.SkyCoordinate
        The sky coordinate.
    """

    loc = "orca"

    if frame_to == "UTM" or frame_to == "ParticleFrame":
        loc = args[5]

    sky_object = kc.build_event(frame_from, *args)
    sky_object = kc.transform_to(sky_object, frame_to, loc)

    return sky_object


def eq_to_utm(ra, dec, date, time, det):
    """Equatorial to UTM frame transformation function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector for the UTM coordinate system, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "equatorial"
    frame_to = "UTM"
    SC = global_transform(frame_from, frame_to, date, time, ra, dec, "deg", det)

    return SC


def eq_to_loc(ra, dec, date, time, det):
    """Equatorial to ParticleFrame frame transformation function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector for the ParticleFrame coordinate system, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "equatorial"
    frame_to = "ParticleFrame"
    SC = global_transform(frame_from, frame_to, date, time, ra, dec, "deg", det)

    return SC


def eq_to_gal(ra, dec, date, time):
    """Equatorial to galactic frame transformation function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "equatorial"
    frame_to = "galactic"
    SC = global_transform(frame_from, frame_to, date, time, ra, dec, "deg")

    return SC


def loc_to_eq(phi, theta, date, time, det):
    """ParticleFrame to equatorial frame transformation function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "ParticleFrame"
    frame_to = "equatorial"
    SC = global_transform(frame_from, frame_to, date, time, theta, phi, "deg", det)

    return SC


def loc_to_utm(phi, theta, date, time, det):
    """ParticleFrame to UTM frame transformation function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "ParticleFrame"
    frame_to = "UTM"
    SC = global_transform(frame_from, frame_to, date, time, theta, phi, "deg", det)

    return SC


def loc_to_gal(phi, theta, date, time, det):
    """ParticleFrame to galactic frame transformation function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """

    frame_from = "ParticleFrame"
    frame_to = "galactic"
    SC = global_transform(frame_from, frame_to, date, time, theta, phi, "deg", det)

    return SC


def print_eq_to_utm(ra, dec, date, time, det):
    """Equatorial to UTM frame print function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector for the UTM coordinate system, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    az, ze = get_az_zenith(eq_to_utm(ra, dec, date, time, det))
    print(str(az) + " " + str(ze))


def print_eq_to_loc(ra, dec, date, time, det):
    """Equatorial to ParticleFrame frame print function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector for the ParticleFrame coordinate system, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    phi, theta = get_phi_theta(eq_to_loc(ra, dec, date, time, det))
    print(str(phi) + " " + str(theta))


def print_eq_to_gal(ra, dec, date, time):
    """Equatorial to galactic frame print function

    Parameters
    ----------
    ra : float
        Right ascension in degree of the sky object
    dec : float
        Declination in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    l, b = get_l_b(eq_to_gal(ra, dec, date, time))
    print(str(l) + " " + str(b))


def print_loc_to_eq(phi, theta, date, time, det):
    """ParticleFrame to equatorial frame print function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    ra, dec = get_ra_dec(loc_to_eq(phi, theta, date, time, det))
    print(str(ra) + " " + str(dec))


def print_loc_to_utm(phi, theta, date, time, det):
    """ParticleFrame to UTM frame print function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    az, ze = get_az_zenith(loc_to_utm(phi, theta, date, time, det))
    print(str(az) + " " + str(ze))


def print_loc_to_gal(phi, theta, date, time, det):
    """ParticleFrame to galactic frame print function

    Parameters
    ----------
    phi : float
        Phi in degree of the sky object
    theta : float
        Theta in degree of the sky object
    date : str
        Date of the sky object, format "YYYY-MM-DD"
    time : str
        Time of the sky object, format "HH:MM:SS"
    det : str
    The name of the detector of the sky object, either "antares", "orca" or "arca"

    Returns
    -------
    SC : astropy.SkyCoordinate
        The sky coordinate.
    """
    l, b = get_l_b(loc_to_gal(phi, theta, date, time, det))
    print(str(l) + " " + str(b))


def print_Skycoord(SkyCoord):
    """Print Skycoord object"""
    print(SkyCoord)


def reader_from_file(file):
    """read a csv file into a pandas DataFrame"""
    table = pd.read_csv(file, comment="#")

    return table


def get_frame_name(SC):
    """Get the frame name from a SkyCoord object"""
    return SC.frame.name


def get_obstime(SC):
    """Get the time of observation from a SkyCoord object"""
    return SC.obstime


def split_date_time(dt):
    """Split in date and time a string from the observation time of a SkyCoord object

    Parameters
    ----------
    dt : str
        the date and time string from a SkyCoord object observation time, format "YYYY-MM-DDTHH:MM:SS"

    Returns
    -------
    (date, time): (str, str)
        date and time of the sky object
    """
    date, time = dt.fits.split("T", 1)
    return pd.Series([date, time])


def Skycoord_breaker(data_SC):
    """Break a pandas DataFrame of SkyCoord into a new DataFrame with every parameters (date, time, ra/l/phi/az, dec/b/theta/alt)

    Parameters
    ----------
    data_SC : pandas.DataFrame(SkyCoord)
        pandas DataFrame containing Skycoord object

    Returns
    -------
    data : pandas.DataFrame
        A pandas DataFrame with every parameters of the input SkyCoord object
    """

    sub_sc = pd.DataFrame(data_SC)

    frame = sub_sc.apply(lambda x: get_frame_name(x.SkyCoord_new))
    frame0 = frame[0]

    for i in frame:
        if i != frame0:
            raise ValueError(
                "Non identical frame in list: expect only " + frame0 + " and got " + i
            )

    obstime = sub_sc.apply(lambda x: get_obstime(x.SkyCoord_new))

    data = obstime.apply(lambda x: split_date_time(x))

    data.set_axis(["date", "time"], axis="columns", inplace=True)

    if frame0 == "galactic":
        data["gal_lon"] = sub_sc.apply(lambda x: x.SkyCoord_new.l.deg * 1)
        data["gal_lat"] = sub_sc.apply(lambda x: x.SkyCoord_new.b.deg * 1)
        return data

    elif frame0 == "icrs":
        data["ra"] = sub_sc.apply(lambda x: x.SkyCoord_new.ra.deg * 1)
        data["dec"] = sub_sc.apply(lambda x: x.SkyCoord_new.dec.deg * 1)
        return data

    elif frame0 == "utm":
        data["az"] = sub_sc.apply(lambda x: x.SkyCoord_new.azimuth.deg * 1)
        data["ze"] = sub_sc.apply(lambda x: x.SkyCoord_new.zenith.deg * 1)
        return data

    elif frame0 == "particleframe":
        data["phi"] = sub_sc.apply(lambda x: x.SkyCoord_new.phi.deg * 1)
        data["theta"] = sub_sc.apply(lambda x: x.SkyCoord_new.theta.deg * 1)
        return data

    else:
        raise ValueError("Error: Wrong Skycoord.frame :" + frame0)
        return None


def transform_file(
    file0,
    frame_from,
    frame_to,
    detector_from="orca",
    detector_to="orca",
    name="",
    return_data=False,
):
    """Transform the input file containing coordinate into a new table of those coordinate in a new frame

    Parameters
    ----------
    file0 : str
        The path to the csv file containing the coordinate. Should follow the "km3py/test-data/astro/benchmark" format.
    frame_from : str
        The frame of the coordinate inside file0, either "ParticleFrame" or "UTM" or "equatorial" or "galactic"
    frame_to : str
        The desired frame of the output sky coordinate
    detector_from : str [default = "orca"]
        Detector of the file0 coordinate, either "orca", "arca" or "antares" . Mandatory if using frame_from = "ParticleFrame" or "UTM".
    detector_to : str [default = "orca"]
        Detector to use for the coordinate transformation, either "orca", "arca" or "antares" . Mandatory if using frame_to = "ParticleFrame" or "UTM".
    name : str [default = tempfile]
        path and name of the output file.

    Returns
    -------
    data : csv file
        Csv file containing the pandas dataframe with the transformed coordinate.

    """
    table_read = reader_from_file(file0)

    table_new = kc.transform_to_new_frame(
        table_read, frame_from, frame_to, detector_from, detector_to
    )

    data = [table_new["SkyCoord_new"]]

    data = Skycoord_breaker(data)

    if name == "":
        import tempfile

        path = tempfile.TemporaryDirectory()
        name = "data" + frame_to + ".csv"

    data.to_csv(name, index=False)
    if return_data == True:
        return data


def build_skycoord_list(table, frame, detector="antares"):
    """Transform the input table containing coordinate into a new table of SkyCoord coordinate

    Parameters
    ----------
    table : pandas.DataFrame
        The table from the csv file containing the sky parameter.
    frame : str
        The frame of the coordinate inside the table, either "ParticleFrame" or "UTM" or "equatorial" or "galactic"
    detector : str [default = "antares"]
        Detector of the coordinate inside the table, either "orca", "arca" or "antares" . Mandatory if using frame_from = "ParticleFrame" or "UTM".

    Returns
    -------
    list_evt : pandas.DataFrame(astropy.SkyCoord)
        DataFrame containing astropy.SkyCoord object corresponding to the sky coordinate in the input table.

    """

    if frame == "ParticleFrame":
        list_evt = table.apply(
            lambda x: kc.build_event(
                frame, x.date, x.time, x.theta, x.phi, "deg", detector
            ),
            axis=1,
            result_type="expand",
        )

    if frame == "UTM":
        list_evt = table.apply(
            lambda x: kc.build_event(
                frame, x.date, x.time, x.azimuth, x.zenith, "deg", detector
            ),
            axis=1,
            result_type="expand",
        )

    if frame == "equatorial":
        list_evt = table.apply(
            lambda x: kc.build_event(
                frame, x.date, x.time, x["RA-J2000"], x["DEC-J2000"]
            ),
            axis=1,
            result_type="expand",
        )

    if frame == "galactic":
        list_evt = table.apply(
            lambda x: kc.build_event(frame, x.date, x.time, x.gal_lon, x.gal_lat),
            axis=1,
            result_type="expand",
        )

    if isinstance(list_evt, pd.Series):
        series_ = {"SkyCoord_base": list_evt}
        list_evt = pd.DataFrame(series_)

    list_evt.set_axis(["SkyCoord_base"], axis="columns", inplace=True)

    return list_evt
