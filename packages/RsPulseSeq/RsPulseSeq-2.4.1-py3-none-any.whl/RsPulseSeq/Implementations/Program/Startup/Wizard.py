from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Wizard:
	"""Wizard commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("wizard", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:STARtup:WIZard:ENABle \n
		Snippet: value: bool = driver.program.startup.wizard.get_enable() \n
		Enable this command, if you wish the wizard to open when the software starts. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:STARtup:WIZard:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:STARtup:WIZard:ENABle \n
		Snippet: driver.program.startup.wizard.set_enable(enable = False) \n
		Enable this command, if you wish the wizard to open when the software starts. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:STARtup:WIZard:ENABle {param}')
