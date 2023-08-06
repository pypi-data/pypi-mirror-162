from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PlFm:
	"""PlFm commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plFm", core, parent)

	def get_values(self) -> str:
		"""SCPI: IMPort:PDW:DATA:PLFM:VALues \n
		Snippet: value: str = driver.importPy.pdw.data.plFm.get_values() \n
		Queries the pulse parameter. \n
			:return: values: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:PLFM:VALues?')
		return trim_str_response(response)

	def set_values(self, values: str) -> None:
		"""SCPI: IMPort:PDW:DATA:PLFM:VALues \n
		Snippet: driver.importPy.pdw.data.plFm.set_values(values = '1') \n
		Queries the pulse parameter. \n
			:param values: No help available
		"""
		param = Conversions.value_to_quoted_str(values)
		self._core.io.write(f'IMPort:PDW:DATA:PLFM:VALues {param}')
