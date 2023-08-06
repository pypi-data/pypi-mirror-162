from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Toolbar:
	"""Toolbar commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("toolbar", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:TOOLbar:ENABle \n
		Snippet: value: bool = driver.program.toolbar.get_enable() \n
		No command help available \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:TOOLbar:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:TOOLbar:ENABle \n
		Snippet: driver.program.toolbar.set_enable(enable = False) \n
		No command help available \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:TOOLbar:ENABle {param}')
