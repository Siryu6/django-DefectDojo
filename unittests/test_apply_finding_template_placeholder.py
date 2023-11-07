import sys
import datetime
sys.path.append('..')
from dojo.models import Product, Product_Type
from dojo.models import Engagement
from dojo.models import Test_Type
from dojo.models import Test
from dojo.models import Finding
from dojo.models import Finding_Template
from dojo.models import System_Settings
from django.utils import timezone
from rest_framework.test import APIClient
from .dojo_test_case import DojoTestCase
from django.contrib.auth.models import User


class FindingMother:

    @staticmethod
    def create():
        settings = System_Settings()
        settings.save()

        p = Product()
        p.Name = 'Test Product for placeholder'
        p.Description = 'Product for Testing Apply Template placeholder functionality'
        p.prod_type = Product_Type.objects.get(id=1)
        p.save()

        e = Engagement()
        e.product = p
        e.target_start = timezone.now()
        e.target_end = e.target_start + datetime.timedelta(days=5)
        e.save()

        tt = Test_Type()
        tt.name = 'Temporary Test'
        tt.save()

        t = Test()
        t.engagement = e
        t.test_type = tt
        t.target_start = timezone.now()
        t.target_end = t.target_start + datetime.timedelta(days=5)
        t.save()

        user = FindingTemplatePlaceholderTestUtil.create_user(True)

        f = Finding()
        f.title = 'Finding for Testing Apply Template placeholder functionality'
        f.severity = 'High'
        f.description = 'This output should stay'
        f.test = t
        f.reporter = user
        f.last_reviewed = timezone.now()
        f.last_reviewed_by = user
        f.save()


class FindingTemplateMother:
    @staticmethod
    def create():
        tmp = Finding_Template()
        tmp.title = 'Finding Template for Testing Apply Template placeholder functionality'
        tmp.cwe = 0
        tmp.severity = 'Low'
        tmp.description = '{{original}}'
        tmp.mitigation = 'Finding Template Mitigation'
        tmp.impact = 'Finding Template Impact'
        tmp.findings_to_replace = "Finding for Testing Apply Template placeholder functionality"
        tmp.list_replace = True
        tmp.save()


class FindingTemplatePlaceholderTestUtil:

    def __init__(self):
        pass

    @staticmethod
    def create_user(is_staff):
        user_count = User.objects.count()
        user = User()
        user.is_staff = is_staff
        user.username = 'TestUser' + str(user_count)
        user.save()
        return user


class TestApplyFindingTemplatePlaceHolder(DojoTestCase):
    fixtures = ['dojo_testdata.json']

    def setUp(self):
        # Create the test Finding
        FindingMother.create()
        # Create Template with "list_replace" enabled (with "Test Finding" inside the list)
        FindingTemplateMother.create()

    def test_apply_template_with_placeholder_to_finding(self):
        finding_url = 'api/v2/findings/?id=1'
        client = APIClient()
        response = self.client.get(finding_url)
        # Check that {{original}} placeholder worked
        self.assertEqual(response.json()["results"][0]["description"], 'This output should stay')
        # Check that Title has been replaced by template Title
        self.assertEqual(response.json()["results"][0]["title"], 'Finding Template for Testing Apply Template placeholder functionality')
        # Check Severity has Changed
        self.assertNotEqual(response.json()["results"][0]["severity"], "Low")

