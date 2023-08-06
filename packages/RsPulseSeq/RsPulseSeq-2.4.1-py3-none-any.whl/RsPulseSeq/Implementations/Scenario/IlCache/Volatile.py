from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Volatile:
	"""Volatile commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("volatile", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:ILCache:VOLatile:CLEar \n
		Snippet: driver.scenario.ilCache.volatile.clear() \n
		Deletes the files from the volatile/repository memory. \n
		"""
		self._core.io.write(f'SCENario:ILCache:VOLatile:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:ILCache:VOLatile:CLEar \n
		Snippet: driver.scenario.ilCache.volatile.clear_with_opc() \n
		Deletes the files from the volatile/repository memory. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:ILCache:VOLatile:CLEar', opc_timeout_ms)

	def get_valid(self) -> bool:
		"""SCPI: SCENario:ILCache:VOLatile:VALid \n
		Snippet: value: bool = driver.scenario.ilCache.volatile.get_valid() \n
		Queries whether the volatile/repository memory contains a valid signal file. \n
			:return: valid: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:ILCache:VOLatile:VALid?')
		return Conversions.str_to_bool(response)
