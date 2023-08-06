from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Supress:
	"""Supress commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("supress", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:OUTPut:SUPRess:ENABle \n
		Snippet: value: bool = driver.scenario.output.supress.get_enable() \n
		Enable to prevent waveform recalculation if the RF frequency is changed. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:SUPRess:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:OUTPut:SUPRess:ENABle \n
		Snippet: driver.scenario.output.supress.set_enable(enable = False) \n
		Enable to prevent waveform recalculation if the RF frequency is changed. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:OUTPut:SUPRess:ENABle {param}')
