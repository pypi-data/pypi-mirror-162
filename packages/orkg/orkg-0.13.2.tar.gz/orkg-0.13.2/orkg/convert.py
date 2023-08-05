class JsonLDConverter:
    """
    Custom convertor from ORKG JSON to JSON-LD
    """

    ORKG_PREFIX = "https://orkg.org/"
    CLASS_PREFIX = f"{ORKG_PREFIX}class/"
    RESOURCE_PREFIX = f"{ORKG_PREFIX}resource/"
    PREDICATE_PREFIX = f"{ORKG_PREFIX}property/"

    _blank_node_counter = 1

    def get_blank_node_id(self):
        """
        Creates an incremental blank node identifier for the json-ld structure
        :return: string in the form of _:n{number}
        """
        bn_id = f"_:n{self._blank_node_counter}"
        self._blank_node_counter = self._blank_node_counter + 1
        return bn_id

    def convert_2_jsonld(self, orkg_json: dict):
        """
        Convert an ORKG JSON format to an equivalent JSON-LD format
        :param orkg_json: The root ORKG JSON object
        :return: a json object in the format of JSON-LD
        """
        context = {}
        jsonld = {}
        if 'resource' in orkg_json:
            orkg_json = orkg_json['resource']
        # create dummy blank node
        jsonld['@id'] = self.get_blank_node_id()

        # handle label
        jsonld['label'] = orkg_json['name']
        context['label'] = "http://www.w3.org/2000/01/rdf-schema#label"

        # handle classes
        jsonld['@type'] = [self.CLASS_PREFIX + c for c in orkg_json['classes']]

        # handle values
        self.handle_values(orkg_json['values'], jsonld, context)

        # prepare final jsonld
        jsonld["@context"] = context
        return jsonld

    def handle_values(self, orkg_json: dict, jsonld: dict, context: dict):
        """
        Recursively handle the values part of the ORKG JSON format
        :param orkg_json: the ORKG object to work on
        :param jsonld: the resulting JSON-LD part
        :param context: the accompanying context for JSON-LD
        :return: Nothing, since it operates on the parameter dictionaries
        """
        # add predicates into context
        for prop, url in [(p, self.PREDICATE_PREFIX + p) for p in orkg_json.keys()]:
            context[prop] = url

        # handle each predicate
        for key, entities in orkg_json.items():
            jsonld[key] = []
            for entity in entities:
                jsonld_entity = {}
                # handle @id
                if '@id' in entity:
                    if '@type' in entity:  # TODO: replace with match in python 3.10
                        entity_type = entity['@type']
                        if entity_type == "resource":
                            jsonld_entity['@id'] = self.RESOURCE_PREFIX + entity['@id']
                        elif entity_type == "class":
                            jsonld_entity['@id'] = self.CLASS_PREFIX + entity['@id']
                        elif entity_type == "predicate":
                            jsonld_entity['@id'] = self.PREDICATE_PREFIX + entity['@id']
                        else:
                            # FIXME: the literal value should be looked up and added here properly
                            jsonld_entity['@literal'] = entity['@id']
                    else:
                        if entity['@id'][0] == "R":
                            jsonld_entity['@id'] = self.RESOURCE_PREFIX + entity['@id']
                        else:
                            # FIXME: the literal value should be looked up and added here properly
                            jsonld_entity['@literal'] = entity['@id']

                # handle text
                if 'text' in entity:
                    literal_value = entity['text']
                    if 'datatype' in entity:
                        literal_value = f"{literal_value}^^{jsonld_entity['datatype']}"
                    jsonld[key].append(literal_value)

                # handle label
                if 'label' in entity:
                    jsonld_entity['@id'] = self.get_blank_node_id()
                    jsonld_entity['label'] = entity['label']
                    if 'classes' in entity:
                        jsonld_entity['@type'] = [self.CLASS_PREFIX + c for c in entity['classes']]

                    # handle values
                    if 'values' in entity:
                        self.handle_values(entity["values"], jsonld_entity, context)
                # append newly created json-ld entity property
                if len(jsonld_entity) > 0:
                    jsonld[key].append(jsonld_entity)


if __name__ == '__main__':
    import json
    sample = """{"resource":{"name":"Statistically significant hypothesis test with IRE binding dependent variable on failing and non-failing hearts","classes":["C1007"],"values":{"P27011":[{"label":"http://purl.obolibrary.org/obo/GO_0030350","classes":["URI"]}],"P4003":[{"classes":["C1003"],"values":{"P9003":[{"classes":["C1004"],"values":{"P9004":[{"text":"1.3111247517411605e-08"}]},"label":""}]},"label":"the p-value of the statistical hypothesis test"}],"P4015":[{"label":"data.csv","classes":["C21033"]}]}}}"""
    print(JsonLDConverter().convert_2_jsonld(json.loads(sample)))
