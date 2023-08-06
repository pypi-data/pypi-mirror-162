from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Locpl:
	"""Locpl commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("locpl", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: SETup:LOCPl:ENABle \n
		Snippet: value: bool = driver.setup.locpl.get_enable() \n
		Couples the LO signals. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SETup:LOCPl:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SETup:LOCPl:ENABle \n
		Snippet: driver.setup.locpl.set_enable(enable = False) \n
		Couples the LO signals. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SETup:LOCPl:ENABle {param}')
