from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class System:
	"""System commands group definition. 3 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("system", core, parent)

	@property
	def error(self):
		"""error commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_error'):
			from .Error import Error
			self._error = Error(self._core, self._cmd_group)
		return self._error

	def get_progress(self) -> float:
		"""SCPI: SYSTem:PROGress \n
		Snippet: value: float = driver.system.get_progress() \n
		Queries the signal generation progress status. \n
			:return: progress: float
		"""
		response = self._core.io.query_str('SYSTem:PROGress?')
		return Conversions.str_to_float(response)

	def clone(self) -> 'System':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = System(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
