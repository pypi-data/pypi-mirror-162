from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Refresh:
	"""Refresh commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("refresh", core, parent)

	def set(self) -> None:
		"""SCPI: CPANel:REFResh \n
		Snippet: driver.cpanel.refresh.set() \n
		Refreshes the displayed information. \n
		"""
		self._core.io.write(f'CPANel:REFResh')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: CPANel:REFResh \n
		Snippet: driver.cpanel.refresh.set_with_opc() \n
		Refreshes the displayed information. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CPANel:REFResh', opc_timeout_ms)
