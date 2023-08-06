from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Reset:
	"""Reset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("reset", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:OUTPut:RESet:ENABle \n
		Snippet: value: bool = driver.scenario.output.reset.get_enable() \n
		Restarts the connected instrument on scenario start. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:RESet:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:OUTPut:RESet:ENABle \n
		Snippet: driver.scenario.output.reset.set_enable(enable = False) \n
		Restarts the connected instrument on scenario start. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:OUTPut:RESet:ENABle {param}')
