from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Interleave:
	"""Interleave commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("interleave", core, parent)

	def set(self) -> None:
		"""SCPI: SCENario:INTerleave \n
		Snippet: driver.scenario.interleave.set() \n
		If method RsPulseSeq.Scenario.Cemit.Interleaving.value|method RsPulseSeq.Scenario.Cpdw.interleaving|method RsPulseSeq.
		Scenario.Localized.Interleaving.value|method RsPulseSeq.Scenario.Df.Interleaving.value 1, triggers the calculation of a
		single output file. The output file comprises the individual PDWs or pulses, where overlapping PDWs or pulses within an
		interleaving group are dropped, based on a defined priority. \n
		"""
		self._core.io.write(f'SCENario:INTerleave')

	def set_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:INTerleave \n
		Snippet: driver.scenario.interleave.set_with_opc() \n
		If method RsPulseSeq.Scenario.Cemit.Interleaving.value|method RsPulseSeq.Scenario.Cpdw.interleaving|method RsPulseSeq.
		Scenario.Localized.Interleaving.value|method RsPulseSeq.Scenario.Df.Interleaving.value 1, triggers the calculation of a
		single output file. The output file comprises the individual PDWs or pulses, where overlapping PDWs or pulses within an
		interleaving group are dropped, based on a defined priority. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:INTerleave', opc_timeout_ms)
