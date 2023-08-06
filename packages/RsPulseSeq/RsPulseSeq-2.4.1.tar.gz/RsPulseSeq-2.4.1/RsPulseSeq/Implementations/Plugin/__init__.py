from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Plugin:
	"""Plugin commands group definition. 13 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("plugin", core, parent)

	@property
	def module(self):
		"""module commands group. 0 Sub-classes, 6 commands."""
		if not hasattr(self, '_module'):
			from .Module import Module
			self._module = Module(self._core, self._cmd_group)
		return self._module

	def get_catalog(self) -> str:
		"""SCPI: PLUGin:CATalog \n
		Snippet: value: str = driver.plugin.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('PLUGin:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: PLUGin:COMMent \n
		Snippet: value: str = driver.plugin.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('PLUGin:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: PLUGin:COMMent \n
		Snippet: driver.plugin.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'PLUGin:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: PLUGin:CREate \n
		Snippet: driver.plugin.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'PLUGin:CREate {param}')

	def load(self, load: str) -> None:
		"""SCPI: PLUGin:LOAD \n
		Snippet: driver.plugin.load(load = '1') \n
		Loads the selected DLL file, see also 'Plug-in programming API'. \n
			:param load: string File path incl. file name and extension
		"""
		param = Conversions.value_to_quoted_str(load)
		self._core.io.write(f'PLUGin:LOAD {param}')

	def get_name(self) -> str:
		"""SCPI: PLUGin:NAME \n
		Snippet: value: str = driver.plugin.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('PLUGin:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: PLUGin:NAME \n
		Snippet: driver.plugin.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'PLUGin:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: PLUGin:REMove \n
		Snippet: driver.plugin.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'PLUGin:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: PLUGin:SELect \n
		Snippet: value: str = driver.plugin.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('PLUGin:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: PLUGin:SELect \n
		Snippet: driver.plugin.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'PLUGin:SELect {param}')

	def clone(self) -> 'Plugin':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Plugin(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
