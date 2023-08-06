from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Plugin:
	"""Plugin commands group definition. 6 total commands, 1 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plugin", core, parent)

	@property
	def variable(self):
		"""variable commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_variable'):
			from .Variable import Variable
			self._variable = Variable(self._core, self._cmd_group)
		return self._variable

	def get_name(self) -> str:
		"""SCPI: DESTination:PLUGin:NAME \n
		Snippet: value: str = driver.destination.plugin.get_name() \n
		Sets the name of the export plug-in. \n
			:return: name: string
		"""
		response = self._core.io.query_str('DESTination:PLUGin:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: DESTination:PLUGin:NAME \n
		Snippet: driver.destination.plugin.set_name(name = '1') \n
		Sets the name of the export plug-in. \n
			:param name: string
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'DESTination:PLUGin:NAME {param}')

	def clone(self) -> 'Plugin':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Plugin(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
