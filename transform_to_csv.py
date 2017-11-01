import csv
import xml.etree.cElementTree as ET
import re
import codecs
import cerberus
import pprint
import schema

OSM_PATH = "sample_divide_by10.osm"
# OSM_PATH = "beijing_china.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    for tag in element.iter('tag'):
        record = {}
        record['id'] = element.attrib['id']
        record['value'] = tag.attrib['v']
        key = tag.attrib['k']
        first_colon_index = key.find(':')
        if first_colon_index >= 0:
            record['key'] = key[first_colon_index + 1:]
            record['type'] = key[0:first_colon_index]
        else:
            record['key'] = key
            record['type'] = default_tag_type
        tags.append(record)
    if element.tag == 'node':
        for node_field in node_attr_fields:
            node_attribs[node_field] = element.attrib[node_field]
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for way_attr_field in way_attr_fields:
            way_attribs[way_attr_field] = element.attrib[way_attr_field]
        position = 0
        for node in element.iter('nd'):
            way_node_record = {}
            way_node_record['id'] = element.attrib['id']
            way_node_record['node_id'] = node.attrib['ref']
            way_node_record['position'] = position
            position += 1
            way_nodes.append(way_node_record)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

class UnicodeDictWriter(csv.DictWriter, object):
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        raise Exception(message_string.format(field, error_string))

def get_element(osm_file,tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def process_map(file_in, validate):
    with codecs.open(NODES_PATH, 'w') as nodes_file,\
        codecs.open(NODE_TAGS_PATH, 'w') as node_tags_file,\
        codecs.open(WAYS_PATH, 'w') as ways_file,\
        codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file,\
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file:
#             nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
#             node_tags_writer = csv.DictWriter(node_tags_file, NODE_TAGS_FIELDS)
#             ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
#             way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)
#             way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
            
            nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
            node_tags_writer = UnicodeDictWriter(node_tags_file, NODE_TAGS_FIELDS)
            ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
            way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
            way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
            
            nodes_writer.writeheader()
            node_tags_writer.writeheader()
            ways_writer.writeheader()
            way_tags_writer.writeheader()
            way_nodes_writer.writeheader()
            
            validator = cerberus.Validator()
            
            for element in get_element(file_in, tags=('node', 'way')):
                el = shape_element(element)
                if el:
                    if validate is True:
                        validate_element(el, validator)
                    if element.tag == 'node':
                        nodes_writer.writerow(el['node'])
                        node_tags_writer.writerows(el['node_tags'])
                    if element.tag == 'way':
                        ways_writer.writerow(el['way'])
                        way_tags_writer.writerows(el['way_tags'])
                        way_nodes_writer.writerows(el['way_nodes'])

if __name__ == '__main__':
	process_map(OSM_PATH, validate = True)
