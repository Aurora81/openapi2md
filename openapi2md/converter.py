# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from codecs import open
import json
import yaml


class Converter(object):
    def __init__(self, input_filepath, output_filepath, locale='en'):
        super(Converter, self).__init__()
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath
        self.locale = locale

    def convert(self):
        with open(self.input_filepath, 'r', encoding='utf-8') as f:
            content = yaml.load(f)

        self.ensure_openapi_3(content)

        api = API()
        api.parse(content)
        res = api.format()

        with open(self.output_filepath, 'w', encoding='utf-8') as out:
            out.write(res)

    def ensure_openapi_3(self, content):
        if not content.get('openapi', '').startswith('3.'):
            raise ValueError('Expected an OpenAPI 3 specification file')


class Field(object):
    def __init__(self, name):
        super(Field, self).__init__()
        self.name = name
        self.examples = {}

    def parse(self, seg, data, required=False):
        self.type = seg.get('type', '')
        self.desc = seg.get('description', '')
        self.required = required
        self.example_value = seg.get('example', '')
        required_fields = seg.get('required', [])
        if self.type == 'object':
            self.fields = []
            sorted_items = sorted(seg.get('properties', {}).items(), key=lambda t: t[0])
            for name, value in sorted_items:
                required = True if name in required_fields else False
                field = Field(name)
                field.parse(value, data, required)
                self.fields.append(field)
        elif self.type == 'array':
            value = seg.get('items')
            field = Field('')
            field.parse(value, data, False)
            self.field = field

        self.examples = seg.get('x-examples', {})

    def format(self, level):
        r = ''
        if self.type == 'object':
            if self.name:
                r += '|{level}{field}|{type}|{required}|{description}|\n'.format(
                    level='+' * level,
                    field=self.name,
                    type=self.type,
                    required=self.required,
                    description=self.desc
                )
                level += 1
            for field in self.fields:
                r += field.format(level)
        elif self.type == 'array':
            field = self.field
            r += '|{level}{field}|[{type}]|{required}|{description}|\n'.format(
                level='+' * level,
                field=self.name,
                type=field.type,
                required=self.required,
                description=self.desc
            )
            r += field.format(level + 1)
        else:
            if not self.name:
                return r

            r += '|{level}{field}|{type}|{required}|{description}|\n'.format(
                level='+' * level,
                field=self.name,
                type=self.type,
                required=self.required,
                description=self.desc
            )

        return r

    def example(self):
        if self.examples:
            for k, v in self.examples.items():
                return v

        if self.type == 'object':
            r = {}
            for field in self.fields:
                r[field.name] = field.example()
        elif self.type == 'array':
            field = self.field
            r = [field.example()]
        else:
            if self.example_value:
                r = self.example_value
            else:
                if self.type == "integer" or self.type == "number":
                    r = 0
                elif self.type == "boolean":
                    r = False
                else:
                    r = self.type

        return r


class ComponentSchema(object):
    def __init__(self, name):
        super(ComponentSchema, self).__init__()
        self.name = name

    def parse(self, seg, data):
        self.title = seg.get('title', '')
        self.type = seg.get('type', '')
        self.desc = seg.get('description', '')
        self.tags = seg.get('x-tags', '')

        field = Field('')
        field.parse(seg, data)
        self.field = field

    def format(self, level=0):
        r = '### {name}\n\n'.format(name=self.name)
        if self.desc:
            r += '{desc}\n\n'.format(desc=self.desc)

        r += '**Properties**\n\n'
        r += '|Field|Type|Required|Description|\n'
        r += '|---|---|---|---|\n'
        r += self.field.format(level)
        r += '\n'

        r += '**Example**\n\n'
        r += '```json\n'
        r += json.dumps(self.field.example(), indent=4) + '\n'
        r += '```\n'
        return r

    def example(self):
        r = self.field.example()
        return r


class Parameter(object):
    def __init__(self):
        pass

    def parse(self, seg, data):
        self.name = seg.get('name', '')
        self.type = seg.get('schema', {}).get('type', 'string')
        self.where = seg.get('in', '')
        self.required = seg.get('required', False)
        self.desc = seg.get('description', False)

    def format(self):
        r = '|{field}|{where}|{type}|{required}|{description}|\n'.format(
            field=self.name,
            where=self.where,
            type=self.type,
            required=self.required,
            description=self.desc
        )
        return r


class RequestBody(object):
    def __init__(self, name):
        self.name = name
        self.fmt = []
        self.field = None
        self.content_type = 'application/json'

    def parse(self, seg, data):
        self.desc = seg.get('description', '')
        content = seg.get('content', {})
        schema = content.get('application/json', {}).get('schema', {})
        if not schema:
            schema = content.get('multipart/form-data', {}).get('schema', {})
            if schema:
                self.content_type = 'multipart/form-data'

        if schema:
            self.fmt.append('application/json')
            field = Field('')
            field.parse(schema, data)
            self.field = field
        self.examples = content.get('application/json', {}).get('examples', {})

    def format(self):
        r = ''
        if not self.field:
            return r

        r += 'Body Type: ' + self.content_type + '\n\n'
        r += 'Body Parameter\n\n'
        r += '|Field|Type|Required|Description|\n'
        r += '|---|---|---|---|\n'
        r += self.field.format(level=0)
        r += '\n'
        return r

    def example(self):
        r = ''
        if not self.field and not self.examples:
            return r

        r += 'Body Example\n\n'
        r += '```json\n'
        if self.examples:
            for k, v in self.examples.items():
                r += json.dumps(v.get('value', {}), indent=4) + '\n'
                break
        else:
            r += json.dumps(self.field.example(), indent=4) + '\n'
        r += '```\n'
        return r


class Response(object):
    def __init__(self, name):
        self.name = name
        self.fmt = []
        self.field = None
        self.examples = {}
        self.content_type = 'application/json'

    def parse(self, seg, data):
        self.desc = seg.get('description', '')
        content = seg.get('content', {})
        schema = content.get('application/json', {}).get('schema', {})
        if not schema:
            schema = content.get('multipart/form-data', {}).get('schema', {})
            if schema:
                self.content_type = 'multipart/form-data'

        if schema:
            self.fmt.append('application/json')
            field = Field('')
            field.parse(schema, data)
            self.field = field
        self.examples = content.get('application/json', {}).get('examples', {})

    def format(self):
        r = ''
        if not self.field:
            return r

        r += 'Status Code {name}\n\n'.format(name=self.name)
        r += 'Body Type: ' + self.content_type + '\n\n'
        r += '|Field|Type|Required|Description|\n'
        r += '|---|---|---|---|\n'
        r += self.field.format(level=0)
        r += '\n'
        return r

    def example(self):
        r = ''
        if not self.field and not self.examples:
            return r

        r += '{name} Response\n\n'.format(name=self.name)
        r += '```json\n'
        if self.examples:
            for k, v in self.examples.items():
                r += json.dumps(v.get('value', {}), indent=4) + '\n'
                break
        else:
            r += json.dumps(self.field.example(), indent=4) + '\n'
        r += '```\n'
        return r


class Operation(object):
    def __init__(self, name):
        self.name = name
        self.parameters = []
        self.responses = []
        self.request_body = None

    def parse(self, seg, data):
        self.desc = seg.get('description', '')
        self.summary = seg.get('summary', '')
        self.id = seg.get('operationId', '')
        self.tags = seg.get('tags', [])
        for value in seg.get('parameters', []):
            parameter = Parameter()
            parameter.parse(value, data)
            self.parameters.append(parameter)

        sorted_items = sorted(seg.get('responses', {}).items(), key=lambda t: t[0])
        for name, value in sorted_items:
            response = Response(name)
            response.parse(value, data)
            self.responses.append(response)

        request_body = seg.get('requestBody', {})
        if request_body:
            self.request_body = RequestBody('')
            self.request_body.parse(request_body, data)

    def format(self):
        r = '#### {name}\n\n'.format(name=self.name.upper())
        if self.desc:
            r += '{desc}\n\n'.format(desc=self.desc)
        if self.parameters:
            r += '**Parameters**\n\n'
            r += '|Field|In|Type|Required|Description|\n'
            r += '|---|---|---|---|---|\n'
            for parameter in self.parameters:
                r += parameter.format()
            r += '\n'

        if self.request_body:
            r += '**Request Body**\n\n'
            r += self.request_body.format()
            r += self.request_body.example()

        if self.responses:
            r += '**Responses**\n\n'
            if self.responses:
                r += '|Status|Description|\n'
                r += '|---|---|\n'
                for response in self.responses:
                    r += '|{status}|{desc}|\n'.format(
                        status=response.name,
                        desc=response.desc
                    )
                r += '\n'

            r += '**Response Schema**\n\n'
            for response in self.responses:
                r += response.format()

            r += '**Response Example**\n\n'
            for response in self.responses:
                r += response.example()

        return r


class Path(object):
    def __init__(self, name):
        self.name = name
        self.operations = []
        self.parameters = []

    def parse(self, seg, data):
        sorted_items = sorted(seg.items(), key=lambda t: t[0])
        for name, value in sorted_items:
            if name == 'parameters':
                for v in value:
                    parameter = Parameter()
                    parameter.parse(v, data)
                    self.parameters.append(parameter)
                continue
            operation = Operation(name)
            operation.parse(value, data)
            self.operations.append(operation)

    def format(self):
        r = '### {name}\n\n'.format(name=self.name)
        for operation in self.operations:
            r += operation.format()
        return r


class Component(object):
    def __init__(self):
        self.schemas = []

    def parse(self, seg, data):
        sorted_items = sorted(seg.get('schemas', {}).items(), key=lambda t: t[0])
        for name, value in sorted_items:
            cs = ComponentSchema(name)
            cs.parse(value, data)
            self.schemas.append(cs)

    def format(self):
        r = '## Schemas\n\n'
        for schema in self.schemas:
            r += schema.format()
        return r


class Info():
    def __init__(self):
        self.license = {}
        self.contact = {}

    def parse(self, seg, data):
        self.title = seg.get('title', '')
        self.version = seg.get('version', '')
        self.description = seg.get('description', '')
        self.license = seg.get('license', {})
        self.contact = seg.get('contact', {})

    def format(self):
        r = '# {title}\n\n'.format(title=self.title)
        r += '{description}\n\n'.format(description=self.description)
        if self.contact:
            r += 'Contact:\n\n'
            r += 'Name: {name}\n\n'.format(name=self.contact.get('name', ''))
            r += 'Email: {email}\n\n'.format(email=self.contact.get('email', ''))
        if self.license:
            r += 'License:\n\n'
            r += 'Name: {name}\n\n'.format(name=self.license.get('name', ''))
            r += 'URL: {url}\n\n'.format(url=self.license.get('url', ''))

        return r


class API(object):
    def __init__(self):
        self.info = None
        self.servers = []
        self.paths = []
        self.components = None
        self.security = []
        self.tags = []

    def parse(self, data):
        self.info = Info()
        self.info.parse(data.get('info', {}), data)
        sorted_items = sorted(data.get('paths', {}).items(), key=lambda t: t[0])
        for name, value in sorted_items:
            path = Path(name)
            path.parse(value, data)
            self.paths.append(path)

        component = Component()
        component.parse(data['components'], data)
        self.components = component

    def format(self):
        r = self.info.format()
        if self.paths:
            r += '## API\n\n'
            for path in self.paths:
                r += path.format()
        if self.components:
            r += self.components.format()
        return r
