#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import sys

try:
	OSM_FILE = sys.argv[1]
except IndexError:
	OSM_FILE = 'sample_divide_by10.osm'


phone_number_re = re.compile(r'^((00)?86)?(0?10)?(\d{8})$', re.IGNORECASE)
mobile_phone_number_re = re.compile(r'^((00)?86(10)?)?(1\d{10})$', re.IGNORECASE)

# Since every phone number needs to be cleaned
# to conform to the same rule.
# First decide whether it is an array,
# then call clean_phone_number function to clean each phone number.
def clean(osmfile):
	osm_file = open(osmfile, 'r')
	unnormal_phone_numbers = set()
	for event, element in ET.iterparse(osm_file):
		if element.tag == 'node' or element.tag == 'way':
			for tag in element.iter('tag'):
				if is_phone_number(tag):
					phone = tag.attrib['v']
					if is_array(phone):
						phones = re.split(r';|；|/', phone)
						for phone in phones:
							# audit_phone_number(unnormal_phone_numbers, phone)
							clean_phone_number(phone)
					else:
						# audit_phone_number(unnormal_phone_numbers, phone)
						clean_phone_number(phone)

	osm_file.close()
	print unnormal_phone_numbers
	return unnormal_phone_numbers

def is_phone_number(tag):
	return (tag.attrib['k'] == "phone")

def is_array(phone):
	if re.search(r';|/|；', phone):
		return True
	else:
		return False

# this function is for searching for the incorrect phone numbers
def audit_phone_number(unnormal_phone_numbers, phone):
	phone_number = re.sub(r'\D', "", phone)
	m = phone_number_re.search(phone_number)
	n = mobile_phone_number_re.search(phone_number)
	if (not m) and (not n):
		unnormal_phone_numbers.add(phone_number)
	return unnormal_phone_numbers


def clean_phone_number(phone): 
# uncorrect_phone_numbers will be dropped, 
# while others need to conform to consistency
	phone_number = re.sub(r'\D', "", phone) 
	# non-digit characters are removed to simplify clean process
	m = phone_number_re.search(phone_number)
	n = mobile_phone_number_re.search(phone_number)
	if m:
		cleaned_phone_number = '010-' + m.group(4)
	elif n:
		cleaned_phone_number = n.group(4)
	else:
		cleaned_phone_number = None
	if cleaned_phone_number:
		print phone, '=>', cleaned_phone_number
	else:
		print phone, '=> omitted'
	return cleaned_phone_number 


if __name__ == '__main__':
	clean(OSM_FILE)
