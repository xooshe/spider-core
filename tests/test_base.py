import importlib
import os
import sys
import types
import unittest
from unittest import mock

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")


def _build_django_stubs():
    django = types.ModuleType("django")
    core = types.ModuleType("django.core")
    files = types.ModuleType("django.core.files")
    files_base = types.ModuleType("django.core.files.base")
    serializers = types.ModuleType("django.core.serializers")
    serializers_json = types.ModuleType("django.core.serializers.json")
    validators = types.ModuleType("django.core.validators")
    utils = types.ModuleType("django.utils")
    deconstruct = types.ModuleType("django.utils.deconstruct")

    class ContentFile:
        def __init__(self, *args, **kwargs):
            pass

    class DjangoJSONEncoder:
        def default(self, obj):
            raise TypeError("Object is not JSON serializable")

    class RegexValidator:
        pass

    def deconstructible(cls):
        return cls

    files_base.ContentFile = ContentFile
    serializers_json.DjangoJSONEncoder = DjangoJSONEncoder
    validators.RegexValidator = RegexValidator
    deconstruct.deconstructible = deconstructible

    files.base = files_base
    serializers.json = serializers_json
    core.files = files
    core.serializers = serializers
    core.validators = validators
    utils.deconstruct = deconstruct
    django.core = core
    django.utils = utils

    return {
        "django": django,
        "django.core": core,
        "django.core.files": files,
        "django.core.files.base": files_base,
        "django.core.serializers": serializers,
        "django.core.serializers.json": serializers_json,
        "django.core.validators": validators,
        "django.utils": utils,
        "django.utils.deconstruct": deconstruct,
    }


class SpiderImportTestCase(unittest.TestCase):
    def setUp(self):
        if SRC_DIR not in sys.path:
            sys.path.insert(0, SRC_DIR)
            self._path_inserted = True
        else:
            self._path_inserted = False

        self._stub_modules = _build_django_stubs()
        self._patch = mock.patch.dict(sys.modules, self._stub_modules)
        self._patch.start()
        self._clear_spider_modules()
        self.spider = importlib.import_module("spider")

    def tearDown(self):
        self._clear_spider_modules()
        self._patch.stop()
        if self._path_inserted:
            sys.path.remove(SRC_DIR)

    def _clear_spider_modules(self):
        for module_name in list(sys.modules):
            if module_name == "spider" or module_name.startswith("spider."):
                sys.modules.pop(module_name, None)

    def test_spider_package_imports_successfully(self):
        self.assertEqual(self.spider.__name__, "spider")
        self.assertIn("generate_unique_file_name", self.spider.__all__)
        self.assertTrue(hasattr(self.spider, "Base64"))
        self.assertTrue(hasattr(self.spider, "DefaultJsonEncoder"))

    def test_public_api_exposes_expected_names(self):
        expected_names = {
            "PaginationData",
            "PaginationRO",
            "Base64",
            "DefaultJsonEncoder",
            "generate_unique_file_name",
            "LocalPhoneNumberValidator",
            "MobileNumberValidator",
            "local_phone_number_validator",
            "mobile_number_validator",
        }
        self.assertEqual(set(self.spider.__all__), expected_names)

        for attribute in expected_names:
            with self.subTest(attribute=attribute):
                self.assertTrue(hasattr(self.spider, attribute))

    def test_generate_unique_file_name_returns_uploads_path(self):
        result = self.spider.generate_unique_file_name(None, "example.png")
        self.assertRegex(result, r"^uploads/[^/]+\.png$")

    def test_dataclass_exports_can_be_instantiated(self):
        pagination_data = self.spider.PaginationData(page=1, take=25)
        pagination_ro = self.spider.PaginationRO(
            items=[1, 2, 3], pageInfo=pagination_data
        )

        self.assertEqual(pagination_data.page, 1)
        self.assertEqual(pagination_data.take, 25)
        self.assertEqual(pagination_ro.items, [1, 2, 3])
        self.assertIs(pagination_ro.pageInfo, pagination_data)


if __name__ == "__main__":
    unittest.main()
