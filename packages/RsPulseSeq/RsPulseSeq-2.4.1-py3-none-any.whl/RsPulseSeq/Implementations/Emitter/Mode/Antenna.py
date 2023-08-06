from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Antenna:
	"""Antenna commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("antenna", core, parent)

	def clear(self) -> None:
		"""SCPI: EMITter:MODE:ANTenna:CLEar \n
		Snippet: driver.emitter.mode.antenna.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'EMITter:MODE:ANTenna:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: EMITter:MODE:ANTenna:CLEar \n
		Snippet: driver.emitter.mode.antenna.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EMITter:MODE:ANTenna:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: EMITter:MODE:ANTenna \n
		Snippet: value: str = driver.emitter.mode.antenna.get_value() \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:return: antenna: string
		"""
		response = self._core.io.query_str('EMITter:MODE:ANTenna?')
		return trim_str_response(response)

	def set_value(self, antenna: str) -> None:
		"""SCPI: EMITter:MODE:ANTenna \n
		Snippet: driver.emitter.mode.antenna.set_value(antenna = '1') \n
		Assigns an existing antenna pattern, see method RsPulseSeq.Antenna.catalog. \n
			:param antenna: string
		"""
		param = Conversions.value_to_quoted_str(antenna)
		self._core.io.write(f'EMITter:MODE:ANTenna {param}')
