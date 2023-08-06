from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Adb:
	"""Adb commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adb", core, parent)

	def get_state(self) -> bool:
		"""SCPI: INSTrument:ADB:STATe \n
		Snippet: value: bool = driver.instrument.adb.get_state() \n
		Defines the instrument that holds the adjustment data of hardware setup. \n
			:return: state: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('INSTrument:ADB:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""SCPI: INSTrument:ADB:STATe \n
		Snippet: driver.instrument.adb.set_state(state = False) \n
		Defines the instrument that holds the adjustment data of hardware setup. \n
			:param state: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'INSTrument:ADB:STATe {param}')
