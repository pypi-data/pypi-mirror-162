from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Lserver:
	"""Lserver commands group definition. 4 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lserver", core, parent)

	@property
	def apply(self):
		"""apply commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_apply'):
			from .Apply import Apply
			self._apply = Apply(self._core, self._cmd_group)
		return self._apply

	def get_options(self) -> str:
		"""SCPI: LSERver:OPTions \n
		Snippet: value: str = driver.lserver.get_options() \n
		Queries the available options. \n
			:return: options: string
		"""
		response = self._core.io.query_str('LSERver:OPTions?')
		return trim_str_response(response)

	def get_ready(self) -> bool:
		"""SCPI: LSERver:READy \n
		Snippet: value: bool = driver.lserver.get_ready() \n
		Queries the status of the license server. \n
			:return: ready: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('LSERver:READy?')
		return Conversions.str_to_bool(response)

	def get_status(self) -> str:
		"""SCPI: LSERver:STATus \n
		Snippet: value: str = driver.lserver.get_status() \n
		Queries the status of the license server. \n
			:return: status: string
		"""
		response = self._core.io.query_str('LSERver:STATus?')
		return trim_str_response(response)

	def clone(self) -> 'Lserver':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Lserver(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
