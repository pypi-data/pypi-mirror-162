from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Adjustments:
	"""Adjustments commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adjustments", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:ADJustments:ENABle \n
		Snippet: value: bool = driver.program.adjustments.get_enable() \n
		Enables using the path loss compensation function. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:ADJustments:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:ADJustments:ENABle \n
		Snippet: driver.program.adjustments.set_enable(enable = False) \n
		Enables using the path loss compensation function. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:ADJustments:ENABle {param}')
