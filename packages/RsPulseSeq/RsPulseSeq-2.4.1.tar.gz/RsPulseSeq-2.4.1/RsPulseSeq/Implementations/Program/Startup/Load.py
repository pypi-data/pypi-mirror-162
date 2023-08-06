from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Load:
	"""Load commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("load", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:STARtup:LOAD:ENABle \n
		Snippet: value: bool = driver.program.startup.load.get_enable() \n
		Sets if a scenario is opened each time the software is started up. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:STARtup:LOAD:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:STARtup:LOAD:ENABle \n
		Snippet: driver.program.startup.load.set_enable(enable = False) \n
		Sets if a scenario is opened each time the software is started up. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:STARtup:LOAD:ENABle {param}')
