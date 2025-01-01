

from SWADL.engine.swadl_constants import VALIDATE_VISIBLE
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_base_section import SWADLPageSection


class HDHSHeader(SWADLPageSection):
    # Purpose: navigation

    def __init__(self, name="HDHSHeader", **kwargs):
        # Purpose: describe the page
        super().__init__(name=name, **kwargs)
        self.url = "https://www.highdeserthumane.org/"

        self.high_desert_humane_society = SWADLControl(
            is_text="High Desert Humane Society",
            name="high desert humane society",
            parent=self,
            selector='span',
            validation={VALIDATE_VISIBLE: True},
        )

        self.HALT_spay_neuter = SWADLControl(
            is_text="H.A.L.T. Spay Neuter",
            name="H.A.L.T. spay neuter",
            parent=self,
            selector='.label-text-bold',
            validation={VALIDATE_VISIBLE: True},
        )

        self.adoption_policies_and_fees = SWADLControl(
            is_text="Adoption Policies and Fees",
            name="adoption policies and fees",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.monthly_rabies_vaccination_clinics_information = SWADLControl(
            is_text="Monthly Rabies Vaccination Clinics Information",
            name="monthly rabies vaccination clinics information",
            parent=self,
            selector='.label-text-bold',
            validation={VALIDATE_VISIBLE: True},
        )

        self.about_us = SWADLControl(
            is_text="About Us",
            name="about us",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.more = SWADLControl(
            is_text="More",
            name="more",
            parent=self,
            selector='.dir-ltr',
            validation={VALIDATE_VISIBLE: True},
        )

        self.services = SWADLControl(
            is_text="Services",
            name="services",
            parent=self,
            selector='#body-element',
            validation={VALIDATE_VISIBLE: False},
        )

        self.donations = SWADLControl(
            is_text="Donations",
            name="donations",
            parent=self,
            selector='#body-element',
            validation={VALIDATE_VISIBLE: False},
        )

        self.volunteer = SWADLControl(
            is_text="Volunteer",
            name="volunteer",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )

        self.education = SWADLControl(
            is_text="Education",
            name="education",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )
        self.news_and_videos = SWADLControl(
            is_text="News and Videos",
            name="news_and_videos",
            parent=self,
            selector='div.page-title.text-overflow',
            validation={VALIDATE_VISIBLE: False},
        )

        # used by self.validate_loaded()
        self.validate_loaded_queue = [self.high_desert_humane_society, self.more]

    def hdhs_header_validate_controls(self, test_data):
        # Purpose: loads page, validate controls
        # Keys: None
        # Emits: "GoogleSearchSection loaded ok": True" = page load validated

        list_of_controls = [
            self.high_desert_humane_society,
            self.HALT_spay_neuter,
            self.adoption_policies_and_fees,
            self.more,
            self.services,
            self.donations,
            self.volunteer,
            self.education,
            self.news_and_videos
        ]


        self.load_page()
        self.driver.maximize_window()

        self.more.mouseover()
        # self.more.click()

        for item in list_of_controls:
            item.validate_visible(timeout=1)
