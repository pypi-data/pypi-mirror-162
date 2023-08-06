from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Repository:
	"""Repository commands group definition. 4 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("repository", core, parent)

	@property
	def enable(self):
		"""enable commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_enable'):
			from .Enable import Enable
			self._enable = Enable(self._core, self._cmd_group)
		return self._enable

	def clear(self) -> None:
		"""SCPI: SCENario:CACHe:REPository:CLEar \n
		Snippet: driver.scenario.cache.repository.clear() \n
		Deletes the files from the volatile/repository memory. \n
		"""
		self._core.io.write(f'SCENario:CACHe:REPository:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CACHe:REPository:CLEar \n
		Snippet: driver.scenario.cache.repository.clear_with_opc() \n
		Deletes the files from the volatile/repository memory. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CACHe:REPository:CLEar', opc_timeout_ms)

	def get_valid(self) -> bool:
		"""SCPI: SCENario:CACHe:REPository:VALid \n
		Snippet: value: bool = driver.scenario.cache.repository.get_valid() \n
		Queries whether the volatile/repository memory contains a valid signal file. \n
			:return: valid: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CACHe:REPository:VALid?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'Repository':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Repository(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
