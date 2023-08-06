from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Mute:
	"""Mute commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mute", core, parent)

	def set(self) -> None:
		"""SCPI: CPANel:MUTE \n
		Snippet: driver.cpanel.mute.set() \n
		Deactivates the RF outputs of all signal generators. \n
		"""
		self._core.io.write(f'CPANel:MUTE')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: CPANel:MUTE \n
		Snippet: driver.cpanel.mute.set_with_opc() \n
		Deactivates the RF outputs of all signal generators. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CPANel:MUTE', opc_timeout_ms)
