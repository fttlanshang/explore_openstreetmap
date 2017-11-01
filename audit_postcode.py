#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import xml.etree.cElementTree as ET
from collections import defaultdict, Counter
import sys

# expected_postcodes = []
try:
	OSM_FILE = sys.argv[1]
except IndexError:
	OSM_FILE = 'sample_divide_by10.osm'

mapping = {
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
	uncorrect_postcodes = Counter()
	for event, element in ET.iterparse(osm_file, events=('start',)):
		if element.tag == 'node' or element.tag == 'way':
			for tag in element.iter('tag'):
				if is_postcode(tag):
					valid_postcode = audit_postcode(uncorrect_postcodes, tag.attrib['v'])
					# The below code gives more information about a specific postcode, 
					# and is helpful in manually modify each wrong postcode
					# if valid_postcode is not True:
					# 	print '______________________'
					# 	for tag in element.iter('tag'):
					# 		print tag.attrib['k'], tag.attrib['v']

	osm_file.close()
	return uncorrect_postcodes

def clean():
	uncorrect_postcodes = audit(OSM_FILE)
	print uncorrect_postcodes
	for postcode, count in uncorrect_postcodes.items():
		correct_postcode = update_postcode(postcode, mapping)
		if correct_postcode:
			print postcode, '=>', correct_postcode
		else:
			print postcode, '=> omitted'

def is_postcode(tag):
	return (tag.attrib['k'] == 'addr:postcode')

def audit_postcode(uncorrect_postcodes, postcode_value):
	if len(postcode_value) == 6:
		if postcode_value.startswith('10'):
			return True
	uncorrect_postcodes[postcode_value] += 1
	return False

def update_postcode(postcode, mapping):
	if postcode in mapping:
		modified_postcode = mapping[postcode]
		return modified_postcode
	else:
		return None 

if __name__ == '__main__':
	# audit(OSM_FILE)
	clean()
	