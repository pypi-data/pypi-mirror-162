from random import shuffle
from tempfile import mkdtemp

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.utils import override_settings
from edc_constants.constants import FEMALE
from edc_registration.models import RegisteredSubject
from edc_sites import add_or_update_django_sites
from edc_sites.single_site import SingleSite
from multisite import SiteID

from edc_randomization.constants import ACTIVE
from edc_randomization.models import RandomizationList
from edc_randomization.randomization_list_importer import (
    RandomizationListAlreadyImported,
    RandomizationListImporter,
)
from edc_randomization.randomization_list_verifier import (
    RandomizationListError,
    RandomizationListVerifier,
)
from edc_randomization.randomizer import (
    AllocationError,
    AlreadyRandomized,
    InvalidAssignment,
    RandomizationError,
    Randomizer,
)
from edc_randomization.site_randomizers import NotRegistered, site_randomizers
from edc_randomization.utils import (
    RandomizationListExporterError,
    export_randomization_list,
)

from ..make_test_list import make_test_list
from ..models import SubjectConsent
from ..randomizers import MyRandomizer

fqdn = "example.clinicedc.org"
all_sites = (
    SingleSite(10, "site_one", title="One", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(20, "site_two", title="Two", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(
        30, "site_three", title="Three", country="uganda", country_code="ug", fqdn=fqdn
    ),
    SingleSite(40, "site_four", title="Four", country="uganda", country_code="ug", fqdn=fqdn),
    SingleSite(50, "site_five", title="Five", country="uganda", country_code="ug", fqdn=fqdn),
)


@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=True,
)
class TestRandomizer(TestCase):
    import_randomization_list = False
    site_names = [x.name for x in all_sites]

    def setUp(self):
        super().setUp()
        add_or_update_django_sites(sites=all_sites)
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)

    def populate_list(
        self, randomizer_name=None, site_names=None, per_site=None, overwrite_site=None
    ):
        randomizer = site_randomizers.get(randomizer_name)
        make_test_list(
            full_path=randomizer.get_randomization_list_fullpath(),
            site_names=site_names or self.site_names,
            per_site=per_site,
        )
        randomizer.import_list(overwrite=True)
        if overwrite_site:
            site = Site.objects.get_current()
            randomizer.model_cls().objects.update(site_name=site.name)

    @override_settings(SITE_ID=SiteID(40))
    def test_(self):
        randomizer = site_randomizers.get("default")
        randomizer.import_list()

    @override_settings(SITE_ID=SiteID(40))
    def test_with_consent_insufficient_data(self):
        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        self.assertRaises(
            RandomizationError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=None,
        )

    @override_settings(SITE_ID=SiteID(40))
    def test_with_consent(self):
        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        try:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {str(e)}.")

    @override_settings(SITE_ID=SiteID(40))
    def test_with_gender_and_consent(self):
        class RandomizerWithGender(Randomizer):
            def __init__(self, gender=None, **kwargs):
                self.gender = gender
                super().__init__(**kwargs)

            @property
            def extra_required_attrs(self):
                return dict(gender=self.gender)

        randomizer = site_randomizers.get("default")
        randomizer.import_list()
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, gender=FEMALE, user_created="erikvw"
        )
        try:
            RandomizerWithGender(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                gender=FEMALE,
                user=subject_consent.user_created,
            )
        except Exception as e:
            self.fail(f"Exception unexpectedly raised. Got {str(e)}.")

    @override_settings(SITE_ID=SiteID(40))
    def test_with_list_selects_first(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        first_obj = RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        self.assertEqual(rando.sid, first_obj.sid)

    @override_settings(SITE_ID=SiteID(40))
    def test_updates_registered_subject(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        first_obj = RandomizationList.objects.all().first()
        rs = RegisteredSubject.objects.get(subject_identifier="12345")
        self.assertEqual(rs.subject_identifier, first_obj.subject_identifier)
        self.assertEqual(rs.sid, str(first_obj.sid))
        self.assertEqual(rs.randomization_datetime, first_obj.allocated_datetime)
        self.assertEqual(rs.randomization_list_model, first_obj._meta.label_lower)

    @override_settings(SITE_ID=SiteID(40))
    def test_updates_list_obj_as_allocated(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        first_obj = RandomizationList.objects.all().first()
        self.assertEqual(first_obj.subject_identifier, "12345")
        self.assertTrue(first_obj.allocated)
        self.assertIsNotNone(first_obj.allocated_user)
        self.assertEqual(first_obj.allocated_user, subject_consent.user_created)
        self.assertEqual(first_obj.allocated_datetime, subject_consent.consent_datetime)
        self.assertGreater(first_obj.modified, subject_consent.created)

    @override_settings(SITE_ID=SiteID(40))
    def test_cannot_rerandomize(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        first_obj = RandomizationList.objects.all().first()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        self.assertEqual(rando.sid, first_obj.sid)
        self.assertRaises(
            AlreadyRandomized,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )

    @override_settings(SITE_ID=SiteID(40))
    def test_error_condition1(self):
        """Assert raises if RegisteredSubject not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        rando.registered_subject.sid = None
        rando.registered_subject.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        self.assertEqual(cm.exception.code, "edc_randomization.randomizationlist")

    @override_settings(SITE_ID=SiteID(40))
    def test_error_condition2(self):
        """Assert raises if RandomizationList not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", user_created="erikvw"
        )
        rando = Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        rando.registered_subject.sid = None
        rando.registered_subject.save()
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        self.assertEqual(cm.exception.code, "edc_randomization.randomizationlist")

    def test_error_condition3(self):
        """Assert raises if RandomizationList not updated correctly."""
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        RandomizationList.objects.update(subject_identifier=None)
        with self.assertRaises(AlreadyRandomized) as cm:
            Randomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        self.assertEqual(cm.exception.code, "edc_registration.registeredsubject")

    def test_subject_does_not_exist(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        RegisteredSubject.objects.all().delete()
        self.assertRaises(
            RandomizationError,
            Randomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    def test_str(self):
        self.populate_list(randomizer_name="default", overwrite_site=True)
        site = Site.objects.get_current()
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="12345", site=site, user_created="erikvw"
        )
        Randomizer(
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_created,
        )
        obj = RandomizationList.objects.all().first()
        self.assertTrue(str(obj))

    @override_settings(SITE_ID=SiteID(40))
    def test_for_sites(self):
        """Assert that allocates by site correctly."""

        site = None
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)

        model_cls = MyRandomizer.model_cls()
        model_cls.objects.all().delete()
        self.populate_list(
            randomizer_name=MyRandomizer.name, site_names=self.site_names, per_site=5
        )
        site_names = [obj.site_name for obj in model_cls.objects.all()]
        shuffle(site_names)
        self.assertEqual(len(site_names), len(self.site_names * 5))
        # consent and randomize 5 for each site
        for index, site_name in enumerate(site_names):
            site = Site.objects.get(name=site_name)
            subject_consent = SubjectConsent.objects.create(
                subject_identifier=f"12345{index}", site=site, user_created="erikvw"
            )
            MyRandomizer(
                subject_identifier=subject_consent.subject_identifier,
                report_datetime=subject_consent.consent_datetime,
                site=subject_consent.site,
                user=subject_consent.user_created,
            )
        # assert consented subjects were allocated SIDs in the
        # correct order per site.
        for site_name in site_names:
            randomized_subjects = [
                (obj.subject_identifier, str(obj.sid))
                for obj in model_cls.objects.filter(
                    allocated_site__name=site_name, subject_identifier__isnull=False
                ).order_by("sid")
            ]
            for index, obj in enumerate(
                SubjectConsent.objects.filter(site__name=site_name).order_by(
                    "consent_datetime"
                )
            ):
                rs = RegisteredSubject.objects.get(subject_identifier=obj.subject_identifier)
                self.assertEqual(obj.subject_identifier, randomized_subjects[index][0])
                self.assertEqual(rs.sid, randomized_subjects[index][1])

        # clear out any unallocated
        model_cls.objects.filter(subject_identifier__isnull=True).delete()

        # assert raises on next attempt to randomize
        subject_consent = SubjectConsent.objects.create(
            subject_identifier="ABCDEF",
            site=site,
            user_created="erikvw",
            user_modified="erikvw",
        )
        self.assertRaises(
            AllocationError,
            MyRandomizer,
            subject_identifier=subject_consent.subject_identifier,
            report_datetime=subject_consent.consent_datetime,
            site=subject_consent.site,
            user=subject_consent.user_modified,
        )

    @override_settings(SITE_ID=SiteID(40))
    def test_not_loaded(self):
        try:
            RandomizationListVerifier(randomizer_name=Randomizer.name)
        except RandomizationListError as e:
            self.assertIn("Randomization list has not been loaded", str(e))
        else:
            self.fail("RandomizationListError unexpectedly NOT raised")

    @override_settings(SITE_ID=SiteID(40))
    def test_cannot_overwrite(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)
        make_test_list(
            full_path=MyRandomizer.get_randomization_list_fullpath(),
            site_names=self.site_names,
            count=5,
        )
        randomizer = site_randomizers.get(MyRandomizer.name)
        randomizer.import_list()
        self.assertRaises(RandomizationListAlreadyImported, randomizer.import_list)

    @override_settings(SITE_ID=SiteID(40))
    def test_can_overwrite_explicit(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)
        make_test_list(
            full_path=MyRandomizer.get_randomization_list_fullpath(),
            site_names=self.site_names,
            count=5,
        )
        randomizer = site_randomizers.get(MyRandomizer.name)
        try:
            randomizer.import_list(overwrite=True)
        except RandomizationListAlreadyImported:
            self.fail("RandomizationListImportError unexpectedly raised")

    @override_settings(SITE_ID=SiteID(40))
    def test_invalid_assignment(self):
        site_randomizers._registry = {}
        site_randomizers.register(MyRandomizer)

        MyRandomizer.get_randomization_list_fullpath()
        make_test_list(
            full_path=MyRandomizer.get_randomization_list_fullpath(),
            site_names=self.site_names,
            # change to a different assignments
            assignments=[100, 101],
            count=5,
        )
        self.assertRaises(InvalidAssignment, MyRandomizer.import_list)

    @override_settings(SITE_ID=SiteID(40))
    def test_invalid_sid(self):
        self.populate_list(randomizer_name="default")
        # change to a different starting SID
        obj = RandomizationList.objects.all().order_by("sid").first()
        obj.sid = 99999
        obj.save()

        with self.assertRaises(RandomizationListError) as cm:
            RandomizationListVerifier(randomizer_name=Randomizer.name)
        self.assertIn("Randomization list has invalid SIDs", str(cm.exception))

    @override_settings(SITE_ID=SiteID(40))
    def test_invalid_count(self):
        site = Site.objects.get_current()
        # change number of SIDs in DB
        self.populate_list(randomizer_name="default")
        RandomizationList.objects.create(sid=100, assignment=ACTIVE, site_name=site.name)
        self.assertEqual(RandomizationList.objects.all().count(), 51)
        with self.assertRaises(RandomizationListError) as cm:
            RandomizationListVerifier(randomizer_name=Randomizer.name)
        self.assertIn("Randomization list count is off", str(cm.exception))

    @override_settings(SITE_ID=SiteID(40))
    def test_get_randomizer_cls(self):
        site_randomizers._registry = {}
        self.assertRaises(NotRegistered, site_randomizers.get, MyRandomizer.name)
        site_randomizers.register(MyRandomizer)
        try:
            site_randomizers.get(MyRandomizer.name)
        except NotRegistered:
            self.fail("NotRegistered unexpectedly raised")

    @override_settings(SITE_ID=SiteID(40))
    def test_randomization_list_importer(self):
        randomizer_cls = site_randomizers.get("default")

        make_test_list(
            full_path=randomizer_cls.get_randomization_list_fullpath(),
            site_names=self.site_names,
        )

        importer = RandomizationListImporter(randomizer_cls, dryrun=True, verbose=True)
        importer.import_list()
        self.assertEqual(randomizer_cls.model_cls().objects.all().count(), 0)

        importer = RandomizationListImporter(randomizer_cls, verbose=True)
        importer.import_list()
        self.assertGreater(randomizer_cls.model_cls().objects.all().count(), 0)

    @override_settings(SITE_ID=SiteID(40), EXPORT_FOLDER=mkdtemp())
    def test_randomization_list_exporter(self):
        user = get_user_model().objects.create(
            username="me", is_superuser=False, is_staff=True
        )
        randomizer_cls = site_randomizers.get("default")
        make_test_list(
            full_path=randomizer_cls.get_randomization_list_fullpath(),
            site_names=self.site_names,
        )
        importer = RandomizationListImporter(randomizer_cls, verbose=True)
        importer.import_list()
        self.assertRaises(RandomizationListExporterError, export_randomization_list, "default")
        self.assertRaises(
            RandomizationListExporterError,
            export_randomization_list,
            "default",
            username=user.username,
        )
        user = get_user_model().objects.create(
            username="you", is_superuser=True, is_staff=True
        )
        path = export_randomization_list("default", username=user.username)
        with open(path) as f:
            n = 0
            for line in f:
                n += 1
                if "str" in line:
                    break
        self.assertEqual(n, 51)
