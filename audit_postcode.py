#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import xml.etree.cElementTree as ET
from collections import defaultdict, Counter
import sys

try:
	OSM_FILE = sys.argv[1]
except IndexError:
	OSM_FILE = 'sample_divide_by10.osm'

postcode_mapping = {
	'10060': '100600',
	'10040': '100040',
	'10080': '100080',
	'1111': '100013',
	'110101': '100101',
	'3208': '100022',
	'110023': '100000'
}

def audit(osmfile):
	osm_file = open(osmfile, 'r')
	incorrect_postcodes = Counter()
	for event, element in ET.iterparse(osm_file, events=('start',)):
		if element.tag == 'node' or element.tag == 'way':
			for tag in element.iter('tag'):
				if is_postcode(tag):
					valid_postcode = audit_postcode(incorrect_postcodes, tag.attrib['v'])
					# The below code gives more information about a specific postcode, 
					# and is helpful in manually modify each wrong postcode
					# if valid_postcode is not True:
					# 	print '______________________'
					# 	for tag in element.iter('tag'):
					# 		print tag.attrib['k'], tag.attrib['v']

	osm_file.close()
	return incorrect_postcodes

# This is one way for cleaning: iterate all and find all incorrect_postcodes,
# then correct them. 
# Another way of cleaning postcode is used in transform_to_csv.py.
def clean():
	incorrect_postcodes = audit(OSM_FILE)
	print incorrect_postcodes
	for postcode, count in incorrect_postcodes.items():
		correct_postcode = update_postcode(postcode, postcode_mapping)
		if correct_postcode:
			print postcode, '=>', correct_postcode
		else:
			print postcode, '=> omitted'

# decide whether the tag describes a postcode
def is_postcode(tag):
	return (tag.attrib['k'] == 'addr:postcode')

# decide whether it is a corrct postcode or not
# a right postcode is 6-digit long, ans startswith '10'
def is_correct_postcode(postcode_value):
	if len(postcode_value) == 6:
		if postcode_value.startswith('10'):
			return True
	return False

# If the postcode is correct, return True; 
# else record this postcode
def audit_postcode(incorrect_postcodes, postcode_value):
	if is_correct_postcode(postcode_value):
		return True
	incorrect_postcodes[postcode_value] += 1
	return False

# Use the mapping to correct the postcode,
# If it's not in mapping dict, then drop it
def update_postcode(postcode, postcode_mapping):
	if postcode in postcode_mapping:
		modified_postcode = postcode_mapping[postcode]
		return modified_postcode
	else:
		return None 

if __name__ == '__main__':
	# audit(OSM_FILE)
	clean()
	