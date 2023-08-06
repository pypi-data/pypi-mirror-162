from django.db.models.fields.related import ForeignKey, ManyToManyField, OneToOneField
from django.core.exceptions import FieldError

from simple_excel.engines import ExcelEngine


class MethodField:
    def __init__(self, method_name: str, label: str):
        self.method_name = method_name
        self.label = label


class WriterOption:
    def __init__(self, options=None):
        self.model = getattr(options, "model", None)
        self.fields = getattr(options, "fields", None)


class WriterMetaclass(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        if not getattr(new_class, "Meta", False):
            return new_class

        opts = new_class._meta = WriterOption(getattr(new_class, "Meta", None))

        method_fields = {}

        # collect method fields
        for name, value in attrs.items():
            if isinstance(value, MethodField) and name in opts.fields:
                method_fields[name] = value

        new_class.method_fields = method_fields
        model = opts.model

        model_fields = [f.name for f in model._meta.fields]

        for field_name in opts.fields:
            if field_name not in model_fields and field_name not in method_fields:
                raise FieldError(
                    f"field {field_name} is not in model {model} fields and is not a method either."
                    f"Ensure that field {field_name} exists in {model} model or it's method exists"
                )

            if field_name not in method_fields:
                field = model._meta.get_field(field_name)
                if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField)):
                    raise FieldError(
                        f"field {field.name} is instance of {field.__class__}."
                        "ForeignKey, ManyToMany, OneToOne fields are not supported."
                        "Use MethodField instead"
                    )

        return new_class


class BaseWriter:
    def __init__(self, queryset=None, filename=None):
        self.model = self._meta.model
        self.fields = self._meta.fields
        self.engine_class = ExcelEngine
        self.engine = None
        self.filename = filename

        if filename is None:
           self.filename = self.model.__name__

        if queryset is None:
            self.queryset = self.model.objects.all()
        else:
            self.queryset = queryset

        self.object_fields = []

        model_fields = [f.name for f in self.model._meta.fields]
        for field in self.fields:
            if field in model_fields:
                self.object_fields.append(field)

    def write(self):
        self.engine = self.engine_class()
        self.engine.write(self.get_headers(), self.get_body())

    def get_response(self):
        self.write()
        return self.engine.get_response(self.filename)

    def get_headers(self):
        """
        returns fields' verbose name if it is model field else returns method field label,
        """
        headers = []

        for field in self.fields:
            if field in self.object_fields:
                verbose_name = self.model._meta.get_field(field).verbose_name
                headers.append(verbose_name)
            else:
                field: MethodField = self.method_fields.get(field)
                headers.append(field.label)

        return headers

    def get_body(self):
        body = []
        for obj in self.queryset:
            row = []
            for field in self.fields:
                if field in self.object_fields:

                    row.append(getattr(obj, field))

                else:
                    method = getattr(self, self.method_fields.get(field).method_name)
                    row.append(method(obj))

            body.append(row)
        return body


class Writer(BaseWriter, metaclass=WriterMetaclass):
    pass
