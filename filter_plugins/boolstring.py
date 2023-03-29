#!/usr/bin/python

def as_on_off(value, icaps=True):
	"""
	Return 'On' or 'Off' according to the (assumed-bool) value.
	"""

	if (value):
		str = 'On' if icaps else 'on'
	else:
		str = 'Off' if icaps else 'off'

	return str


class FilterModule(object):

	def filters(self):
		return {
			'as_on_off': as_on_off
		}
