from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Scan:
	"""Scan commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scan", core, parent)

	def clear(self) -> None:
		"""SCPI: EMITter:MODE:SCAN:CLEar \n
		Snippet: driver.emitter.mode.scan.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'EMITter:MODE:SCAN:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: EMITter:MODE:SCAN:CLEar \n
		Snippet: driver.emitter.mode.scan.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'EMITter:MODE:SCAN:CLEar', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: EMITter:MODE:SCAN \n
		Snippet: value: str = driver.emitter.mode.scan.get_value() \n
		Assigns an antenna scan, see method RsPulseSeq.Scan.create. \n
			:return: scan: string
		"""
		response = self._core.io.query_str('EMITter:MODE:SCAN?')
		return trim_str_response(response)

	def set_value(self, scan: str) -> None:
		"""SCPI: EMITter:MODE:SCAN \n
		Snippet: driver.emitter.mode.scan.set_value(scan = '1') \n
		Assigns an antenna scan, see method RsPulseSeq.Scan.create. \n
			:param scan: string
		"""
		param = Conversions.value_to_quoted_str(scan)
		self._core.io.write(f'EMITter:MODE:SCAN {param}')
