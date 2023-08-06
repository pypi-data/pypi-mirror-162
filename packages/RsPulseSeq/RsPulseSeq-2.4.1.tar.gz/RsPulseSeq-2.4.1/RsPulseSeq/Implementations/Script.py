from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Script:
	"""Script commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("script", core, parent)

	def set_add(self, add: str) -> None:
		"""SCPI: SCRipt:ADD \n
		Snippet: driver.script.set_add(add = '1') \n
		No command help available \n
			:param add: No help available
		"""
		param = Conversions.value_to_quoted_str(add)
		self._core.io.write(f'SCRipt:ADD {param}')
