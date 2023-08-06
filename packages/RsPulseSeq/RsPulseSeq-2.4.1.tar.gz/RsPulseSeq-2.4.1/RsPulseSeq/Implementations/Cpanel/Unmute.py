from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Unmute:
	"""Unmute commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("unmute", core, parent)

	def set(self) -> None:
		"""SCPI: CPANel:UNMute \n
		Snippet: driver.cpanel.unmute.set() \n
		Activates the RF outputs of all signal generators. \n
		"""
		self._core.io.write(f'CPANel:UNMute')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: CPANel:UNMute \n
		Snippet: driver.cpanel.unmute.set_with_opc() \n
		Activates the RF outputs of all signal generators. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CPANel:UNMute', opc_timeout_ms)
