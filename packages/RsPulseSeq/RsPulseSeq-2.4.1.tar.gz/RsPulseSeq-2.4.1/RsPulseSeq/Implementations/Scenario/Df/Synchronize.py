from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Synchronize:
	"""Synchronize commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("synchronize", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SCENario:DF:SYNChronize:ENABle \n
		Snippet: value: bool = driver.scenario.df.synchronize.get_enable() \n
		Enables synchronized setup. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:DF:SYNChronize:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:DF:SYNChronize:ENABle \n
		Snippet: driver.scenario.df.synchronize.set_enable(enable = False) \n
		Enables synchronized setup. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:DF:SYNChronize:ENABle {param}')
