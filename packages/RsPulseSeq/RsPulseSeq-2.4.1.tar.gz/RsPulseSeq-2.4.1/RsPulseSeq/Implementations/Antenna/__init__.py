from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Antenna:
	"""Antenna commands group definition. 87 total commands, 1 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("antenna", core, parent)

	@property
	def model(self):
		"""model commands group. 14 Sub-classes, 4 commands."""
		if not hasattr(self, '_model'):
			from .Model import Model
			self._model = Model(self._core, self._cmd_group)
		return self._model

	def get_catalog(self) -> str:
		"""SCPI: ANTenna:CATalog \n
		Snippet: value: str = driver.antenna.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('ANTenna:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: ANTenna:COMMent \n
		Snippet: value: str = driver.antenna.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('ANTenna:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: ANTenna:COMMent \n
		Snippet: driver.antenna.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'ANTenna:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: ANTenna:CREate \n
		Snippet: driver.antenna.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'ANTenna:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: ANTenna:NAME \n
		Snippet: value: str = driver.antenna.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('ANTenna:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: ANTenna:NAME \n
		Snippet: driver.antenna.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'ANTenna:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: ANTenna:REMove \n
		Snippet: driver.antenna.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'ANTenna:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: ANTenna:SELect \n
		Snippet: value: str = driver.antenna.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('ANTenna:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: ANTenna:SELect \n
		Snippet: driver.antenna.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'ANTenna:SELect {param}')

	def clone(self) -> 'Antenna':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Antenna(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
