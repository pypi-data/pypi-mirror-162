from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Subitem:
	"""Subitem commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("subitem", core, parent)

	def get_current(self) -> float:
		"""SCPI: SCENario:LOCalized:SUBitem:CURRent \n
		Snippet: value: float = driver.scenario.localized.subitem.get_current() \n
		No command help available \n
			:return: current: float Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:LOCalized:SUBitem:CURRent?')
		return Conversions.str_to_float(response)

	def set_current(self, current: float) -> None:
		"""SCPI: SCENario:LOCalized:SUBitem:CURRent \n
		Snippet: driver.scenario.localized.subitem.set_current(current = 1.0) \n
		No command help available \n
			:param current: float Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(current)
		self._core.io.write(f'SCENario:LOCalized:SUBitem:CURRent {param}')

	def get_select(self) -> float:
		"""SCPI: SCENario:LOCalized:SUBitem:SELect \n
		Snippet: value: float = driver.scenario.localized.subitem.get_select() \n
		No command help available \n
			:return: select: float Range: 1 to 4096
		"""
		response = self._core.io.query_str('SCENario:LOCalized:SUBitem:SELect?')
		return Conversions.str_to_float(response)

	def set_select(self, select: float) -> None:
		"""SCPI: SCENario:LOCalized:SUBitem:SELect \n
		Snippet: driver.scenario.localized.subitem.set_select(select = 1.0) \n
		No command help available \n
			:param select: float Range: 1 to 4096
		"""
		param = Conversions.decimal_value_to_str(select)
		self._core.io.write(f'SCENario:LOCalized:SUBitem:SELect {param}')
