from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Generator:
	"""Generator commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("generator", core, parent)

	def clear(self) -> None:
		"""SCPI: SCENario:GENerator:CLEar \n
		Snippet: driver.scenario.generator.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'SCENario:GENerator:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: SCENario:GENerator:CLEar \n
		Snippet: driver.scenario.generator.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SCENario:GENerator:CLEar', opc_timeout_ms)

	def get_path(self) -> float:
		"""SCPI: SCENario:GENerator:PATH \n
		Snippet: value: float = driver.scenario.generator.get_path() \n
		Selects the signal path that will play the generated signal. \n
			:return: path: float Range: 1 to 32
		"""
		response = self._core.io.query_str('SCENario:GENerator:PATH?')
		return Conversions.str_to_float(response)

	def set_path(self, path: float) -> None:
		"""SCPI: SCENario:GENerator:PATH \n
		Snippet: driver.scenario.generator.set_path(path = 1.0) \n
		Selects the signal path that will play the generated signal. \n
			:param path: float Range: 1 to 32
		"""
		param = Conversions.decimal_value_to_str(path)
		self._core.io.write(f'SCENario:GENerator:PATH {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:GENerator \n
		Snippet: value: str = driver.scenario.generator.get_value() \n
		Sets the signal generator. \n
			:return: generator: string Use the command GENerator:CATalog? to query a list of configured generator.
		"""
		response = self._core.io.query_str('SCENario:GENerator?')
		return trim_str_response(response)

	def set_value(self, generator: str) -> None:
		"""SCPI: SCENario:GENerator \n
		Snippet: driver.scenario.generator.set_value(generator = '1') \n
		Sets the signal generator. \n
			:param generator: string Use the command GENerator:CATalog? to query a list of configured generator.
		"""
		param = Conversions.value_to_quoted_str(generator)
		self._core.io.write(f'SCENario:GENerator {param}')
