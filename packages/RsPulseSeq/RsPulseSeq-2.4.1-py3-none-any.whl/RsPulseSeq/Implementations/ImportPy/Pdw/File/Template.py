from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Template:
	"""Template commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("template", core, parent)

	def load(self) -> None:
		"""SCPI: IMPort:PDW:FILE:TEMPlate:LOAD \n
		Snippet: driver.importPy.pdw.file.template.load() \n
		Loads the selected file. \n
		"""
		self._core.io.write(f'IMPort:PDW:FILE:TEMPlate:LOAD')

	def load_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IMPort:PDW:FILE:TEMPlate:LOAD \n
		Snippet: driver.importPy.pdw.file.template.load_with_opc() \n
		Loads the selected file. \n
		Same as load, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IMPort:PDW:FILE:TEMPlate:LOAD', opc_timeout_ms)

	def save(self) -> None:
		"""SCPI: IMPort:PDW:FILE:TEMPlate:SAVE \n
		Snippet: driver.importPy.pdw.file.template.save() \n
		Stores the selected file. \n
		"""
		self._core.io.write(f'IMPort:PDW:FILE:TEMPlate:SAVE')

	def save_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: IMPort:PDW:FILE:TEMPlate:SAVE \n
		Snippet: driver.importPy.pdw.file.template.save_with_opc() \n
		Stores the selected file. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'IMPort:PDW:FILE:TEMPlate:SAVE', opc_timeout_ms)

	def get_value(self) -> str:
		"""SCPI: IMPort:PDW:FILE:TEMPlate \n
		Snippet: value: str = driver.importPy.pdw.file.template.get_value() \n
		Sets or queries the name of the used import template file. \n
			:return: template: absolute file path and filename, incl. file extension
		"""
		response = self._core.io.query_str('IMPort:PDW:FILE:TEMPlate?')
		return trim_str_response(response)

	def set_value(self, template: str) -> None:
		"""SCPI: IMPort:PDW:FILE:TEMPlate \n
		Snippet: driver.importPy.pdw.file.template.set_value(template = '1') \n
		Sets or queries the name of the used import template file. \n
			:param template: absolute file path and filename, incl. file extension
		"""
		param = Conversions.value_to_quoted_str(template)
		self._core.io.write(f'IMPort:PDW:FILE:TEMPlate {param}')
