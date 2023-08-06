from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Volatile:
	"""Volatile commands group definition. 4 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("volatile", core, parent)

	@property
	def release(self):
		"""release commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_release'):
			from .Release import Release
			self._release = Release(self._core, self._cmd_group)
		return self._release

	@property
	def restore(self):
		"""restore commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_restore'):
			from .Restore import Restore
			self._restore = Restore(self._core, self._cmd_group)
		return self._restore

	def clear(self) -> None:
		"""SCPI: SCENario:CACHe:VOLatile:CLEar \n
		Snippet: driver.scenario.cache.volatile.clear() \n
		Deletes the files from the volatile/repository memory. \n
		"""
		self._core.io.write(f'SCENario:CACHe:VOLatile:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CACHe:VOLatile:CLEar \n
		Snippet: driver.scenario.cache.volatile.clear_with_opc() \n
		Deletes the files from the volatile/repository memory. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CACHe:VOLatile:CLEar', opc_timeout_ms)

	def get_valid(self) -> bool:
		"""SCPI: SCENario:CACHe:VOLatile:VALid \n
		Snippet: value: bool = driver.scenario.cache.volatile.get_valid() \n
		Queries whether the volatile/repository memory contains a valid signal file. \n
			:return: valid: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:CACHe:VOLatile:VALid?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'Volatile':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Volatile(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
