from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class User:
	"""User commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("user", core, parent)

	@property
	def csv(self):
		"""csv commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_csv'):
			from .Csv import Csv
			self._csv = Csv(self._core, self._cmd_group)
		return self._csv

	def clear(self) -> None:
		"""SCPI: ANTenna:MODel:USER:CLEar \n
		Snippet: driver.antenna.model.user.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'ANTenna:MODel:USER:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: ANTenna:MODel:USER:CLEar \n
		Snippet: driver.antenna.model.user.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'ANTenna:MODel:USER:CLEar', opc_timeout_ms)

	def load(self, load: str) -> None:
		"""SCPI: ANTenna:MODel:USER:LOAD \n
		Snippet: driver.antenna.model.user.load(load = '1') \n
		Loads a custom antenna pattern file. \n
			:param load: string
		"""
		param = Conversions.value_to_quoted_str(load)
		self._core.io.write(f'ANTenna:MODel:USER:LOAD {param}')

	def clone(self) -> 'User':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = User(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
