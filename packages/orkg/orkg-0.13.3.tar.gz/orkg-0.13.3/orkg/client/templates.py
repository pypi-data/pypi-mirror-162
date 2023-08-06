from orkg.utils import NamespacedClient
from orkg.out import OrkgResponse
from orkg.convert import JsonLDConverter
from typing import Dict, List, Union, Tuple, Optional
import re
from tqdm import tqdm
import json
import types
import keyword
import datetime
import logging

NATIVE_TYPES = ['Number', 'String', 'Boolean', 'Integer', 'Date', 'URI']


def pre_process_string(string: str) -> str:
    lower_string = string.lower().replace(' ', '_')
    res = re.sub(r'\W+', '', lower_string)
    return res


def check_against_keywords(string: str) -> str:
    """
    Checks a string against python keywords.
    If a keyword is found, it is postfixed with a '_template'.
    """
    if string in keyword.kwlist:
        return string + '_template'
    return string


def clean_up_dict(dictionary: dict) -> dict:
    """
    replaces the key 'name' with 'label' inside the 'resource' object.
    then strips the root key 'resource' and returns the inner dictionary.
    """
    dictionary = dictionary['resource']
    dictionary['label'] = dictionary['name']
    del dictionary['name']
    return dictionary


def remove_empty_values(dictionary: dict):
    if 'values' not in dictionary['resource']:
        return
    for _, value in dictionary['resource']['values'].items():
        for v in value:
            if not bool(v):
                value.remove(v)


def map_type_to_pythonic_type(value_type: str) -> str:
    if value_type == 'Number':
        return 'Union[int, float, complex]'
    elif value_type == 'Boolean':
        return 'bool'
    elif value_type == 'Integer':
        return 'int'
    elif value_type == 'Date':
        return 'datetime.date'
    else:
        return 'str'


class ObjectStatement(object):
    # Optionals
    label: Optional[str]
    classes: Optional[List[str]]
    text: Optional[str]
    datatype: Optional[str]
    values: Optional[List]
    name: Optional[str]
    # Must have
    predicate_id: str
    template_id: str

    def __init__(self, predicate_id: str, template_id: str):
        self.predicate_id = predicate_id
        self.template_id = template_id
        self.label = None
        self.classes = None
        self.text = None
        self.datatype = None
        self.values = None
        self.name = None

    @staticmethod
    def create_main(name: str, classes: List[str] = None) -> 'ObjectStatement':
        statement = ObjectStatement('', '')
        statement.set_main_statement(name, classes)
        return statement

    @property
    def is_main_statement(self) -> bool:
        return self.name is not None

    def set_main_statement(self, name: str, classes: List[str] = None):
        self.name = name
        self.classes = classes

    def set_literal(self, text: str, datatype: Optional[str] = None):
        self.text = text
        self.datatype = datatype

    def set_nested_statement(self, statement: 'ObjectStatement'):
        self.set_resource(statement.label, statement.classes)
        for value in statement.values:
            self.add_value(value)

    def set_resource(self, label: str, classes: List[str] = None):
        self.label = label
        self.classes = classes

    def add_value(self, value: 'ObjectStatement'):
        if self.values is None:
            self.values = []
        self.values.append(value)

    def values_to_statements(self) -> str:
        if self.values is None:
            return '{}'
        return '{' + ', '.join([f'"{v.predicate_id}": [{{{v.to_statement()}}}]' for v in self.values]) + '}'

    def to_statement(self) -> str:
        statement = ""
        if self.text is not None:
            statement += f'"text": {self.text}'
            if self.datatype is not None:
                statement += f', "datatype": "{self.datatype}"'
        elif self.label is not None:
            statement += f'"label": {self.label}'
            if self.classes is not None:
                statement += f', "classes": {self.classes}'
            if self.values is not None:
                statement += f', "values": {self.values_to_statements()} '
        return statement

    def serialize(self) -> str:
        if self.is_main_statement:
            return f'{{ "resource": {{ "name": "{self.name}", "classes": {self.classes}, "values": {self.values_to_statements()} }} }}'
        else:
            return f'"{self.predicate_id}": [{{{self.to_statement()}}}]'


class TemplateInstance(object):
    """
    A class that takes a dictionary in the constructor
    With methods to serialize the dictionary to a file, pretty print it, and send it to the KG.
    """
    def __init__(self, template_dict, orkg_client) -> None:
        self.template_dict = template_dict
        self.client = orkg_client
        self.preprocess_dict()

    def preprocess_dict(self):
        if isinstance(self.template_dict, str):
            self.template_dict = self.template_dict.strip("'<>() ").replace('\'', '\"')
            self.template_dict = json.loads(self.template_dict)

    def serialize_to_file(self, file_path: str, format: str = "orkg") -> None:
        """
        Serializes the template to a file.
        :param format: the format of the serialization (default: "orkg", possible: "json-ld")
        :param file_path: the file path to save the template to
        """
        with open(file_path, 'w') as f:
            if format.lower().strip() == "json-ld":
                json.dump(JsonLDConverter().convert_2_jsonld(self.template_dict), f, indent=4)
            else:
                json.dump(self.template_dict, f, indent=4)

    def pretty_print(self, format: str = "orkg") -> None:
        """
        Pretty prints the template to the console.
        :param format: the format of the printed text (default: "orkg", possible: "json-ld")
        """
        if format.lower().strip() == "json-ld":
            print(json.dumps(JsonLDConverter().convert_2_jsonld(self.template_dict), indent=4))
        else:
            print(json.dumps(self.template_dict, indent=4))

    def save(self) -> OrkgResponse:
        """
        Saves the template to the server.
        :return: The OrkgResponse from the server
        """
        return self.client.objects.add(params=self.template_dict)

    @staticmethod
    def parse_dict(dictionary: Dict, obj: ObjectStatement) -> None:
        if 'resource' in dictionary:
            # This is a complete resource and not a nested one
            dictionary = dictionary['resource']
            obj.set_resource(dictionary['name'], dictionary['classes'])
            if 'values' in dictionary:
                dictionary = dictionary['values']
        for key, values in dictionary.items():
            for value in values:
                sub_obj = ObjectStatement(key, obj.template_id)
                obj.add_value(sub_obj)
                if 'text' in value:
                    datatype = value.get('datatype', None)
                    sub_obj.set_literal(f"\"{value['text']}\"", datatype)
                elif 'label' in value:
                    classes = value.get('classes', None)
                    sub_obj.set_resource(f"\"{value['label']}\"", classes)
                    if 'values' in value:
                        TemplateInstance.parse_dict(value['values'], sub_obj)


class TemplateComponent:
    predicate_id: str
    predicate_label: str
    value_class_id: Optional[str]
    value_class_label: Optional[str]
    is_of_custom_type: bool
    min_cardinality: Optional[int]
    max_cardinality: Optional[int]
    is_nested_template: bool
    nested_template_target: Optional[str]

    # private properties
    _orkg_client: NamespacedClient

    def __init__(self, orkg_client, component_id: str):
        self._orkg_client = orkg_client
        component_statements = orkg_client.statements.get_by_subject(subject_id=component_id).content
        # Set predicate info
        predicate = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentProperty', component_statements)
        )[0]['object']
        self.predicate_id = predicate['id']
        self.predicate_label = predicate['label']
        # Set class value, id, and label
        value_class = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentValue', component_statements)
        )
        if len(value_class) == 0:
            self.value_class_id = 'String'
            self.value_class_label = 'Text'
            self.is_of_custom_type = False
        else:
            value_class = value_class[0]['object']
            self.value_class_id = value_class['id']
            self.value_class_label = value_class['label']
            self.is_of_custom_type = True if self.value_class_id not in NATIVE_TYPES else False
        # Set cardinality of the property
        max_cardinality = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentOccurrenceMax', component_statements)
        )
        self.max_cardinality = None if len(max_cardinality) == 0 else max_cardinality[0]['object']['label']
        mix_cardinality = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentOccurrenceMin', component_statements)
        )
        self.mix_cardinality = None if len(mix_cardinality) == 0 else mix_cardinality[0]['object']['label']
        # Set if the component is nested template
        if not self.is_of_custom_type:
            self.is_nested_template = False
        else:
            template_classes = orkg_client.statements.get_by_object_and_predicate(object_id=self.value_class_id,
                                                                                  predicate_id='TemplateOfClass').content
            if len(template_classes) == 0:
                self.is_nested_template = False
            else:
                self.is_nested_template = True
                self.nested_template_target = template_classes[0]['subject']['id']

    def get_clean_name(self) -> str:
        return pre_process_string(check_against_keywords(self.predicate_label))

    def get_return_type(self) -> str:
        if self.is_nested_template:
            return 'TemplateInstance'
        return map_type_to_pythonic_type(self.value_class_id)

    def get_property_as_function_parameter(self) -> str:
        clean_label = self.get_clean_name()
        return_type = self.get_return_type()
        return f'{clean_label}: {return_type}'

    def get_param_documentation(self) -> str:
        if self.is_nested_template:
            target_template = Template.find_or_create_template(self._orkg_client, self.nested_template_target)
            return f':param {self.get_clean_name()}: a nested template, use orkg.templates.{target_template.get_template_name_as_function_name()}'
        else:
            # component is not nested template, return normal documentation
            return f':param {self.get_clean_name()}: a parameter of type {self.value_class_label}'

    def create_object_statement(self) -> ObjectStatement:
        to_str = self.get_return_type() == 'datetime.date'
        value = self.get_clean_name()
        statement = ObjectStatement(self.predicate_id, "UNKNOWN")  # FIXME: template_id is unknown in this scope
        if not self.is_nested_template:
            if self.is_of_custom_type:
                statement.set_resource(
                    label=f'str({value})' if to_str else value,
                    classes=[self.value_class_id]
                )
            else:
                statement.set_literal(
                    text=f'str({value})' if to_str else value,
                    datatype=None  # FIXME: datatype is not set for literals
                )
        return statement

    def __str__(self):
        return f'{"N" if self.is_nested_template else ""}Property(id="{self.predicate_id}", label="{self.predicate_label}", class="{self.value_class_id}", cardinality=({self.min_cardinality}, {self.max_cardinality}))'


class Template(object):
    # Static variable to keep track of all templates
    templates: Dict = {}

    # Instance variables
    template_class: str
    is_formatted: bool
    template_id: str
    template_name: str
    components: List[TemplateComponent]

    def __init__(self, orkg_client, template_id: str):
        # Fetch template statements
        self.components = []
        template_statements = orkg_client.statements.get_by_subject(subject_id=template_id).content
        # Iterate over template statements and create template components
        components = filter(lambda x: x['predicate']['id'] == 'TemplateComponent', template_statements)
        for component in components:
            self.components.append(TemplateComponent(orkg_client, component['object']['id']))
        # Set template class
        self.template_class = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateOfClass', template_statements)
        )[0]['object']['id']
        # Set template info
        self.template_id = template_id
        self.template_name = orkg_client.resources.by_id(id=template_id).content['label']
        self.is_formatted = len(
            list(filter(lambda x: x['predicate']['id'] == 'TemplateLabelFormat', template_statements))
        ) > 0
        # Register template to the global templates dict
        Template.templates[template_id] = self

    @staticmethod
    def find_or_create_template(orkg_client, template_id: str) -> 'Template':
        """
        Check if template is in registry, if yes return it.
        Otherwise, instantiate a new template.
        """
        if template_id in Template.templates:
            return Template.templates[template_id]
        else:
            return Template(orkg_client, template_id)

    def get_params_as_function_params(self) -> Tuple[str, str]:
        """
        Returns a tuple of the function parameters for the template.
        The first element is the function parameters as a string,
        the second element is the function docstring as a string.
        """
        params = ', '.join([c.get_property_as_function_parameter() for c in self.components])
        if not self.is_formatted:
            params = f'label: str, {params}'
            if params.strip()[-1] == ',':
                params = params.strip()[:-1]
        params_docstring = '\n\t'.join(
            [
                comp.get_param_documentation()
                for comp in self.components
            ]
        )
        if not self.is_formatted:
            params_docstring = f':param label: the label of the resource of type string\n\t{params_docstring}'
        return params, params_docstring

    def get_template_name_as_function_name(self) -> str:
        return check_against_keywords(pre_process_string(self.template_name))

    def create_api_object_values_and_classes(self) -> Tuple[str, str]:
        """
        Returns the API object values for the template.
        """
        properties = [c.create_object_statement() for c in self.components]
        #  return f""""values": {{{','.join(properties)}}}""", f'"classes": ["{self.template_class}"]'
        return f""""values": {{{','.join([p.serialize() for p in properties])}}}""", f'"classes": ["{self.template_class}"]'

    def create_api_object(self):
        """
        Returns the complete ORKG API object for the template as string.
        """
        values, classes = self.create_api_object_values_and_classes()
        object_json = f"""{{
                "resource": {{
                    "name": {'""' if self.is_formatted else 'label'},
                    {classes},
                    {values}
                }}
            }}"""
        return object_json

    def __str__(self):
        return f'Template(id="{self.template_id}", class="{self.template_class}", components= "{len(self.components)} comps."))'


class OTFFunctionWriter(object):

    @staticmethod
    def implement_function(
            orkg_context: NamespacedClient,
            template_id: str
    ):
        template = Template.find_or_create_template(orkg_context.client, template_id)
        params, params_docstring = template.get_params_as_function_params()
        object_json = template.create_api_object()
        lookup_map = {component.get_clean_name(): component.predicate_id for component in template.components}
        function_name = check_against_keywords(pre_process_string(template.template_name))
        new_method = f'''
def {function_name}(self, {params}) -> TemplateInstance:
    """ Creates a template of type {template_id} ({template.template_name})

    {params_docstring}
    :return: a string representing the resource ID of the newly created resource
    """
    lookup_map = {lookup_map}
    obj = ObjectStatement.create_main({'""' if template.is_formatted else 'label'}, ['{template.template_class}'])
    TemplateInstance.parse_dict({object_json},obj)
    obj = TemplateInstance(obj.serialize(), self.client).template_dict
    for param_name, nested_template in {{k: v for k, v in locals().items() if isinstance(v, TemplateInstance)}}.items():
        predicate_id = lookup_map[param_name]
        if 'values' not in obj['resource']:
            obj['resource']['values'] = {{}}
        if not predicate_id in obj['resource']['values']:
            obj['resource']['values'][predicate_id] = []
        obj['resource']['values'][predicate_id].append(clean_up_dict(nested_template.template_dict))
    remove_empty_values(obj)
    return TemplateInstance(obj, self.client)

orkg_context.client.templates.{function_name} = types.MethodType( {function_name}, orkg_context )
orkg_context.client.templates.materialized_templates.append('{function_name}')
                    '''
        logging.debug(new_method)
        exec(new_method)


class TemplatesClient(NamespacedClient):
    materialized_templates: List[str] = []

    def materialize_template(self, template_id: str):
        """
        Materialize a singular ORKG template as python function
        :param template_id: the template id
        :return: True if everything is OK
        """
        return self._fetch_and_build_template_function(template_id)

    def materialize_templates(self, templates: Optional[List[str]] = None):
        """
        Materialize a list of templates (or all templates if not provided)
        :param templates: optional list of templates
        """
        if templates is None:
            templates = [template['id'] for template in
                         self.client.classes.get_resource_by_class(class_id='ContributionTemplate', size=1000).content]
        exclude = ['R12000', 'R38504', 'R108555', 'R111221', 'R111231', 'R70785', 'R48000', 'R111155']  # RF, RP, Comp last 3
        with tqdm(templates, desc='Materializing templates') as pbar:
            for template_id in pbar:
                if template_id not in exclude:
                    self.materialize_template(template_id)

    def _fetch_and_build_template_function(self, template_id: str):
        """
        Internal function to create python digital twins of ORKG templates
        :param template_id: template ID to build
        :return: True if everything is OK
        """
        OTFFunctionWriter.implement_function(self, template_id)
        return True

    def list_templates(self):
        """
        List the set of materialized template functions
        :return: list of strings
        """
        return self.materialized_templates

    def get_template_specifications(self, template_id: str) -> str:
        """
        Return JSON representation of a template's specification (schema)
        :param template_id: the template to lookup
        :return: string representation of a JSON object
        """
        template = Template(self.client, template_id)
        result = {comp.get_clean_name(): f'A value of type ({comp.value_class_label})' for comp in template.components}
        return json.dumps(result, indent=4, sort_keys=True, default=str)

    def create_template_instance(self, template_id: str, instance: Dict) -> str:
        """
        Creates an instance of a given template by filling in
        the specifications of the template with the provided values

        :param template_id: the string representing the template ID
        :param instance: the json object that contains the components of the template instance
        """
        template = Template(self.client, template_id)
        obj = template.create_api_object()
        for key, value in instance.items():
            obj = obj.replace(key, f'"{value}"')
        json_object = json.loads(obj)
        return self.client.objects.add(params=json_object).content['id']
