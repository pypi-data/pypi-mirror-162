from django.test import TestCase
from django.core.exceptions import FieldError

from .base import Writer
from .models import TestModel


ANY_CHAR_REGEX = "[a-zA-Z0-9 .,]"


class WriterTest(TestCase):
    def setUp(self) -> None:
        TestModel.objects.create(
            name="Alberto",
            description="Mielgo",
            age=20
        )

    def test_it_successfully_creates_response(self):
        class TestWriter(Writer):
            class Meta:
                model = TestModel
                fields = ['name', 'description', 'age']

        writer = TestWriter(queryset=TestModel.objects.all())
        writer.get_response()

    def test_it_raises_error_if_foreign_key_field_passes(self):

        with self.assertRaises(FieldError):
            class TestWriter(Writer):
                class Meta:
                    model = TestModel
                    fields = ['name', 'description', 'parent']

    def test_it_raises_error_if_field_does_not_exist(self):
        with self.assertRaises(FieldError):
            class TestWriter(Writer):
                class Meta:
                    model = TestModel
                    fields = ['name', 'description', 'age', 'parent', 'not_existing_field']

