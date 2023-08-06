from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Select:
	"""Select commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("select", core, parent)

	def get_id(self) -> float:
		"""SCPI: IPM:PLUGin:VARiable:SELect:ID \n
		Snippet: value: float = driver.ipm.plugin.variable.select.get_id() \n
		No command help available \n
			:return: idn: No help available
		"""
		response = self._core.io.query_str('IPM:PLUGin:VARiable:SELect:ID?')
		return Conversions.str_to_float(response)

	def set_id(self, idn: float) -> None:
		"""SCPI: IPM:PLUGin:VARiable:SELect:ID \n
		Snippet: driver.ipm.plugin.variable.select.set_id(idn = 1.0) \n
		No command help available \n
			:param idn: No help available
		"""
		param = Conversions.decimal_value_to_str(idn)
		self._core.io.write(f'IPM:PLUGin:VARiable:SELect:ID {param}')

	def get_value(self) -> str:
		"""SCPI: IPM:PLUGin:VARiable:SELect \n
		Snippet: value: str = driver.ipm.plugin.variable.select.get_value() \n
		Selects a plugin variable. \n
			:return: select: string
		"""
		response = self._core.io.query_str('IPM:PLUGin:VARiable:SELect?')
		return trim_str_response(response)

	def set_value(self, select: str) -> None:
		"""SCPI: IPM:PLUGin:VARiable:SELect \n
		Snippet: driver.ipm.plugin.variable.select.set_value(select = '1') \n
		Selects a plugin variable. \n
			:param select: string
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'IPM:PLUGin:VARiable:SELect {param}')
