from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Xtrg:
	"""Xtrg commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xtrg", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:SCENario:XTRG:ENABle \n
		Snippet: value: bool = driver.program.scenario.xtrg.get_enable() \n
		Enables using a separate trigger for scenario start, see method RsPulseSeq.Scenario.Trigger.set. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:SCENario:XTRG:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:SCENario:XTRG:ENABle \n
		Snippet: driver.program.scenario.xtrg.set_enable(enable = False) \n
		Enables using a separate trigger for scenario start, see method RsPulseSeq.Scenario.Trigger.set. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:SCENario:XTRG:ENABle {param}')
