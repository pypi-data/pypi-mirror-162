from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Calculate:
	"""Calculate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("calculate", core, parent)

	def set(self) -> None:
		"""SCPI: SCENario:CALCulate \n
		Snippet: driver.scenario.calculate.set() \n
		Starts the signal calculation. \n
		"""
		self._core.io.write(f'SCENario:CALCulate')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:CALCulate \n
		Snippet: driver.scenario.calculate.set_with_opc() \n
		Starts the signal calculation. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:CALCulate', opc_timeout_ms)
