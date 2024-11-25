

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection


class HDHSHeader(SWADLPageSection):
    # Purpose: hdhs navigation

    def __init__(self, name="HDHSHeader", **kwargs):
        # Purpose: describe the page
        super().__init__(name=name, **kwargs)
        self.url = "https://www.highdeserthumane.org/"

        self.banner = SWADLControl(
            is_text="High Desert Humane Society",
            name="HDHSBanner",
            parent=self,
            selector='span',
            validation={VALIDATE_VISIBLE: True},
        )

        self.banner = SWADLControl(
            is_text="Adoption Policies and Fees",
            name="HDHSBanner",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.banner = SWADLControl(
            is_text="H.A.L.T. Spay Neuter",
            name="HDHSBanner",
            parent=self,
            selector='.label-text-bold',
            validation={VALIDATE_VISIBLE: True},
        )

        self.banner = SWADLControl(
            is_text="More",
            name="Adoption Policies and Fees",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.banner = SWADLControl(
            is_text="Monthly Rabies Vaccination Clinics Information",
            name="HDHSBanner",
            parent=self,
            selector='.label-text-bold',
            validation={VALIDATE_VISIBLE: True},
        )

        self.banner = SWADLControl(
            is_text="About Us",
            name="HDHSBanner",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.more = SWADLControl(
            is_text="More",
            name="HeaderMore",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.services = SWADLControl(
            is_text="Services",
            name="HeaderMore",
            parent=self,
            selector='#body-element',
            validation={VALIDATE_VISIBLE: False},
        )

        self.donations = SWADLControl(
            is_text="Donations",
            name="HeaderMore",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )

        self.volunteer = SWADLControl(
            is_text="Volunteer",
            name="HeaderMore",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )

        self.education = SWADLControl(
            is_text="Education",
            name="HeaderMore",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )
        self.NewsandVideos = SWADLControl(
            is_text="News and Videos",
            name="HeaderMore",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )

        # used by self.validate_loaded()
        self.validate_loaded_queue = [self.banner, self.more]

    def test_HDHS(self, test_data=None):
        list_of_controls = [
            self.banner_header,
            self.banner_More,
            self.banner_Services,
            self.banner_Donations,
            self.banner_Volunteer,
            self.banner_Education,
            self.banner_NewsandVideos
        ]


        # Purpose: loads page if it's not loaded
        # Keys: SEARCH_KEY
        # Emits: "GoogleSearchSection loaded ok": True" = page load validated

         #self.load_page()
         #self.search_box.set_value(value=self.test_data[SEARCH_KEY])
        # self.search_box.submit()
        for item in list_of_controls:
            item.validate_visible(fatal=True, timeout=1)
