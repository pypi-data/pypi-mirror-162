from unittest import TestCase

from km3net_testdata import data_path
import km3astro.toolbox as ktb
import km3astro.testing_tools as ktt
import km3astro.coord as kc


class TestToolBox(TestCase):
    def setUp(self):
        self.det = "antares"
        self.date = "2007-10-04"
        self.time = "03:03:03"
        self.phi = 97.07
        self.theta = 135.0
        self.az = 277.07
        self.ze = 45.00
        self.ra = 70.613
        self.dec = -1.852
        self.l = 198.7
        self.b = -29.298
        self.threshold = 0.02

    def test_tool_box_eq_to_utm(self):

        SC_check = ktb.eq_to_utm(self.ra, self.dec, self.date, self.time, self.det)
        SC_true = kc.build_event(
            "UTM", self.date, self.time, self.az, self.ze, "deg", self.det
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_tool_box_eq_to_loc(self):

        SC_check = ktb.eq_to_loc(self.ra, self.dec, self.date, self.time, self.det)
        SC_true = kc.build_event(
            "ParticleFrame", self.date, self.time, self.theta, self.phi, "deg", self.det
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_tool_box_eq_to_gal(self):

        SC_check = ktb.eq_to_gal(self.ra, self.dec, self.date, self.time)
        SC_true = kc.build_event(
            "galactic", self.date, self.time, self.l, self.b, "deg"
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_tool_box_loc_to_eq(self):

        SC_check = ktb.loc_to_eq(self.phi, self.theta, self.date, self.time, self.det)
        SC_true = kc.build_event(
            "equatorial", self.date, self.time, self.ra, self.dec, "deg"
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_tool_box_loc_to_utm(self):

        SC_check = ktb.loc_to_utm(self.phi, self.theta, self.date, self.time, self.det)
        SC_true = kc.build_event(
            "UTM", self.date, self.time, self.az, self.ze, "deg", self.det
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_tool_box_loc_to_gal(self):

        SC_check = ktb.loc_to_gal(self.phi, self.theta, self.date, self.time, self.det)
        SC_true = kc.build_event(
            "galactic", self.date, self.time, self.l, self.b, "deg"
        )
        sep = ktt.test_Skycoord_separation(SC_true, SC_check)
        if self.threshold < sep:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(sep)
                + " > "
                + str(self.threshold)
            )

    def test_get_az_zenith(self):

        SC_true = kc.build_event(
            "UTM", self.date, self.time, self.az, self.ze, "deg", self.det
        )

        az, ze = ktb.get_az_zenith(SC_true)
        if az != self.az or ze != self.ze:
            raise ValueError(
                "Error:  ktb.get_az_zenith return wrong value : "
                + str(az)
                + " != "
                + str(self.az)
                + " and "
                + str(ze)
                + " != "
                + str(self.ze)
            )

    def test_get_phi_theta(self):

        SC_true = kc.build_event(
            "ParticleFrame", self.date, self.time, self.theta, self.phi, "deg", self.det
        )

        phi, theta = ktb.get_phi_theta(SC_true)
        if phi != self.phi or theta != self.theta:
            raise ValueError(
                "Error:  ktb.get_phi_theta return wrong value : "
                + str(phi)
                + " != "
                + str(self.phi)
                + " and "
                + str(theta)
                + " != "
                + str(self.theta)
            )

    def test_get_ra_dec(self):

        SC_true = kc.build_event(
            "equatorial", self.date, self.time, self.ra, self.dec, "deg"
        )

        ra, dec = ktb.get_ra_dec(SC_true)
        if ra != self.ra or dec != self.dec:
            raise ValueError(
                "Error:  ktb.get_ra_dec return wrong value : "
                + str(ra)
                + " != "
                + str(self.ra)
                + " and "
                + str(dec)
                + " != "
                + str(self.dec)
            )

    def test_get_l_b(self):

        SC_true = kc.build_event(
            "galactic", self.date, self.time, self.l, self.b, "deg"
        )

        l, b = ktb.get_l_b(SC_true)
        if l != self.l or b != self.b:
            raise ValueError(
                "Error:  ktb.get_l_b return wrong value : "
                + str(l)
                + " != "
                + str(self.l)
                + " and "
                + str(b)
                + " != "
                + str(self.b)
            )

    def test_get_frame_name(self):

        SC_true = kc.build_event(
            "galactic", self.date, self.time, self.l, self.b, "deg"
        )

        fname = ktb.get_frame_name(SC_true)
        if fname != "galactic":
            raise ValueError(
                "Error:  ktb.get_frame_name return wrong value : "
                + fname
                + " != "
                + "galactic"
            )

    def test_get_obstime(self):

        SC_true = kc.build_event(
            "galactic", self.date, self.time, self.l, self.b, "deg"
        )

        obstime = ktb.get_obstime(SC_true)
        true_obstime = self.date + "T" + self.time
        if obstime != true_obstime:
            raise ValueError(
                "Error:  ktb.get_obstime return wrong value : "
                + obstime
                + " != "
                + true_obstime
            )

    def test_transform_file(self):

        data = ktb.transform_file(
            data_path("astro/antares_coordinate_systems_benchmark.csv"),
            "equatorial",
            "galactic",
            "antares",
            "antares",
            return_data=True,
        )

        l = data["gal_lon"][0]
        b = data["gal_lat"][0]

        max_l = l - self.l
        max_b = b - self.b

        if max_l > self.threshold or max_b > self.threshold:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(max_l)
                + " / "
                + str(max_b)
                + " > "
                + str(self.threshold)
            )

    def test_build_skycoord_list(self):

        table = ktb.reader_from_file(
            data_path("astro/antares_coordinate_systems_benchmark.csv")
        )

        data = ktb.build_skycoord_list(table, "equatorial", "antares")
        table_gal_to_eq = kc.transform_to_new_frame(
            table, "galactic", "equatorial", "antares", "antares"
        )

        sep = ktt.test_benchmark_conversion(data, table_gal_to_eq)

        max_ = sep.max()

        if max_ > self.threshold:
            raise AssertionError(
                "Error: Maximum angle separation = "
                + str(max_)
                + " > "
                + str(self.threshold)
            )
