"""Views of the collectivo core."""
from rest_framework.views import APIView
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework.decorators import action
from collectivo.version import __version__
from drf_spectacular.utils import extend_schema, OpenApiResponse


class AboutView(APIView):
    """API views of the project version."""

    @extend_schema(responses={200: OpenApiResponse()})
    def get(self, request):
        """Return the current version of the project."""
        data = {
            'version': __version__,
        }
        return Response(data)


# TODO Default does not work yet
# TODO Choices can be big for large datasets
field_attrs = [
    'label', 'help_text',
    'required', 'default',
    'max_length', 'min_length',
    'max_value', 'min_value',
    'read_only', 'write_only',
    'choices',
]

input_types = {
    'CharField': 'text',
    'UUIDField': 'text',
    'URLField': 'url',
    'TextField': 'email',
    'ChoiceField': 'radio',
    'EmailField': 'email',
    'IntegerField': 'number',
    'FloatField': 'number',
    'DateField': 'date',
    'BooleanField': 'checkbox',
    'ManyRelatedField': 'multiselect',
    'PrimaryKeyRelatedField': 'select',
    'PhoneField': 'phone',
    'CountryField': 'country'
}


class SchemaMixin:
    """Adds an action 'schema' to a viewset."""

    @extend_schema(responses={200: OpenApiResponse()})
    @action(detail=False, url_path='schema', url_name='schema',
            permission_classes=[])
    def _schema(self, request):
        """Return model schema."""
        serializer = self.get_serializer_class()()
        data = {}
        for field_name, field_obj in serializer.fields.items():
            field_type = field_obj.__class__.__name__
            data[field_name] = field_data = {
                "field_type": field_type,
                "input_type": input_types[field_type]
            }
            for attr in field_attrs:
                if hasattr(field_obj, attr):
                    value = getattr(field_obj, attr)
                    if value is not empty and value is not None:
                        data[field_name][attr] = value
            if hasattr(serializer, 'schema_attrs') and \
                    field_name in serializer.schema_attrs:
                for key, value in serializer.schema_attrs[field_name].items():
                    data[field_name][key] = value
            # Ensure that read only fields cannot be required
            if field_data.get('read_only') == True:
                field_data['required'] = False
        return Response(data)
