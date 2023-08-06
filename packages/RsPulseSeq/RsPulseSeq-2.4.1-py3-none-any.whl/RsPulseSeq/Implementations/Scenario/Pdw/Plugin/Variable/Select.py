from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ......Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Select:
	"""Select commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("select", core, parent)

	def get_id(self) -> float:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:SELect:ID \n
		Snippet: value: float = driver.scenario.pdw.plugin.variable.select.get_id() \n
		Selects a plugin variable ID. \n
			:return: idn: float
		"""
		response = self._core.io.query_str('SCENario:PDW:PLUGin:VARiable:SELect:ID?')
		return Conversions.str_to_float(response)

	def set_id(self, idn: float) -> None:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:SELect:ID \n
		Snippet: driver.scenario.pdw.plugin.variable.select.set_id(idn = 1.0) \n
		Selects a plugin variable ID. \n
			:param idn: float
		"""
		param = Conversions.decimal_value_to_str(idn)
		self._core.io.write(f'SCENario:PDW:PLUGin:VARiable:SELect:ID {param}')

	def get_value(self) -> str:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:SELect \n
		Snippet: value: str = driver.scenario.pdw.plugin.variable.select.get_value() \n
		Selects a plugin variable. \n
			:return: select: string
		"""
		response = self._core.io.query_str('SCENario:PDW:PLUGin:VARiable:SELect?')
		return trim_str_response(response)

	def set_value(self, select: str) -> None:
		"""SCPI: SCENario:PDW:PLUGin:VARiable:SELect \n
		Snippet: driver.scenario.pdw.plugin.variable.select.set_value(select = '1') \n
		Selects a plugin variable. \n
			:param select: string
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'SCENario:PDW:PLUGin:VARiable:SELect {param}')
