from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Comment:
	"""Comment commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("comment", core, parent)

	def get_enable(self) -> bool:
		"""SCPI: PROGram:COMMent:ENABle \n
		Snippet: value: bool = driver.program.comment.get_enable() \n
		Add timestamp as comment when creating entries. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PROGram:COMMent:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: PROGram:COMMent:ENABle \n
		Snippet: driver.program.comment.set_enable(enable = False) \n
		Add timestamp as comment when creating entries. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'PROGram:COMMent:ENABle {param}')
