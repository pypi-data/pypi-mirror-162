from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Variable:
	"""Variable commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("variable", core, parent)

	def get_catalog(self) -> str:
		"""SCPI: ANTenna:MODel:PLUGin:VARiable:CATalog \n
		Snippet: value: str = driver.antenna.model.plugin.variable.get_catalog() \n
		Queries the variables used in the plugin. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('ANTenna:MODel:PLUGin:VARiable:CATalog?')
		return trim_str_response(response)

	def get_select(self) -> str:
		"""SCPI: ANTenna:MODel:PLUGin:VARiable:SELect \n
		Snippet: value: str = driver.antenna.model.plugin.variable.get_select() \n
		No command help available \n
			:return: select: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:PLUGin:VARiable:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ANTenna:MODel:PLUGin:VARiable:SELect \n
		Snippet: driver.antenna.model.plugin.variable.set_select(select = '1') \n
		No command help available \n
			:param select: No help available
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ANTenna:MODel:PLUGin:VARiable:SELect {param}')

	def get_value(self) -> str:
		"""SCPI: ANTenna:MODel:PLUGin:VARiable:VALue \n
		Snippet: value: str = driver.antenna.model.plugin.variable.get_value() \n
		No command help available \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:PLUGin:VARiable:VALue?')
		return trim_str_response(response)

	def set_value(self, value: str) -> None:
		"""SCPI: ANTenna:MODel:PLUGin:VARiable:VALue \n
		Snippet: driver.antenna.model.plugin.variable.set_value(value = '1') \n
		No command help available \n
			:param value: No help available
		"""
		param = Conversions.value_to_quoted_str(value)
		self._core.io.write(f'ANTenna:MODel:PLUGin:VARiable:VALue {param}')
