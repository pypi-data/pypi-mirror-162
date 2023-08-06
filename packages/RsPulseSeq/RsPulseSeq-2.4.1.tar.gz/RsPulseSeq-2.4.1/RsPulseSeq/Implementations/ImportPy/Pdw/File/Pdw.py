from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pdw:
	"""Pdw commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pdw", core, parent)

	def load(self) -> None:
		"""SCPI: IMPort:PDW:FILE:PDW:LOAD \n
		Snippet: driver.importPy.pdw.file.pdw.load() \n
		Loads the selected file. \n
		"""
		self._core.io.write(f'IMPort:PDW:FILE:PDW:LOAD')

	def load_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IMPort:PDW:FILE:PDW:LOAD \n
		Snippet: driver.importPy.pdw.file.pdw.load_with_opc() \n
		Loads the selected file. \n
		Same as load, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IMPort:PDW:FILE:PDW:LOAD', opc_timeout_ms)

	def save(self) -> None:
		"""SCPI: IMPort:PDW:FILE:PDW:SAVE \n
		Snippet: driver.importPy.pdw.file.pdw.save() \n
		Stores the selected file. \n
		"""
		self._core.io.write(f'IMPort:PDW:FILE:PDW:SAVE')

	def save_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IMPort:PDW:FILE:PDW:SAVE \n
		Snippet: driver.importPy.pdw.file.pdw.save_with_opc() \n
		Stores the selected file. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IMPort:PDW:FILE:PDW:SAVE', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: IMPort:PDW:FILE:PDW \n
		Snippet: value: str = driver.importPy.pdw.file.pdw.get_value() \n
		Sets or queries the name of the used PDW list file. \n
			:return: pdw: absolute file path and filename, incl. file extension
		"""
		response = self._core.io.query_str('IMPort:PDW:FILE:PDW?')
		return trim_str_response(response)

	def set_value(self, pdw: str) -> None:
		"""SCPI: IMPort:PDW:FILE:PDW \n
		Snippet: driver.importPy.pdw.file.pdw.set_value(pdw = '1') \n
		Sets or queries the name of the used PDW list file. \n
			:param pdw: absolute file path and filename, incl. file extension
		"""
		param = Conversions.value_to_quoted_str(pdw)
		self._core.io.write(f'IMPort:PDW:FILE:PDW {param}')
