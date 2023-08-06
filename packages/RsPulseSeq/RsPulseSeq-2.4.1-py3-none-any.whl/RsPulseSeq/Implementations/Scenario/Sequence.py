from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Sequence:
	"""Sequence commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sequence", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:SEQuence:CLEar \n
		Snippet: driver.scenario.sequence.clear() \n
		No command help available \n
		"""
		self._core.io.write(f'SCENario:SEQuence:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:SEQuence:CLEar \n
		Snippet: driver.scenario.sequence.clear_with_opc() \n
		No command help available \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:SEQuence:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: SCENario:SEQuence \n
		Snippet: value: str = driver.scenario.sequence.get_value() \n
		Assigns a pulse sequence, see method RsPulseSeq.Sequence.catalog. \n
			:return: sequence: string
		"""
		response = self._core.io.query_str('SCENario:SEQuence?')
		return trim_str_response(response)

	def set_value(self, sequence: str) -> None:
		"""SCPI: SCENario:SEQuence \n
		Snippet: driver.scenario.sequence.set_value(sequence = '1') \n
		Assigns a pulse sequence, see method RsPulseSeq.Sequence.catalog. \n
			:param sequence: string
		"""
		param = Conversions.value_to_quoted_str(sequence)
		self._core.io.write(f'SCENario:SEQuence {param}')
