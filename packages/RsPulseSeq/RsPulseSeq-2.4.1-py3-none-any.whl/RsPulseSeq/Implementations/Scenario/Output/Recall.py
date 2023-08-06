from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Recall:
	"""Recall commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("recall", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:OUTPut:RECall:ENABle \n
		Snippet: value: bool = driver.scenario.output.recall.get_enable() \n
		Stores the current signal generator configuration as a save/recall file. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:RECall:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:OUTPut:RECall:ENABle \n
		Snippet: driver.scenario.output.recall.set_enable(enable = False) \n
		Stores the current signal generator configuration as a save/recall file. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:OUTPut:RECall:ENABle {param}')
