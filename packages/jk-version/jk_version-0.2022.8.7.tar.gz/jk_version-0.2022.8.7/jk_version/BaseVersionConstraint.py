

# from __future__ import annotations

import re
import os
import typing

from .Version import Version




class BaseVersionConstraint(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def check(self, version:Version) -> bool:
		raise NotImplementedError()
	#

	def toJSON(self) -> list:
		raise NotImplementedError()
	#

	#
	# The default implementation will return itself.
	# Subclasses may overwrite this method with their own simplification logic.
	#
	# @returns		BaseVersionConstraint		Returns a simplified version of this object.
	#
	def simplify(self):		# -> BaseVersionConstraint:
		return self
	#

#






