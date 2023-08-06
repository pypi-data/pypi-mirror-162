from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Sequence:
	"""Sequence commands group definition. 65 total commands, 3 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sequence", core, parent)

	@property
	def item(self):
		"""item commands group. 10 Sub-classes, 11 commands."""
		if not hasattr(self, '_item'):
			from .Item import Item
			self._item = Item(self._core, self._cmd_group)
		return self._item

	@property
	def phase(self):
		"""phase commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import Phase
			self._phase = Phase(self._core, self._cmd_group)
		return self._phase

	@property
	def time(self):
		"""time commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_time'):
			from .Time import Time
			self._time = Time(self._core, self._cmd_group)
		return self._time

	def get_catalog(self) -> str:
		"""SCPI: SEQuence:CATalog \n
		Snippet: value: str = driver.sequence.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('SEQuence:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: SEQuence:COMMent \n
		Snippet: value: str = driver.sequence.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('SEQuence:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: SEQuence:COMMent \n
		Snippet: driver.sequence.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'SEQuence:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: SEQuence:CREate \n
		Snippet: driver.sequence.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'SEQuence:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: SEQuence:NAME \n
		Snippet: value: str = driver.sequence.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('SEQuence:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: SEQuence:NAME \n
		Snippet: driver.sequence.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'SEQuence:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: SEQuence:REMove \n
		Snippet: driver.sequence.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'SEQuence:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: SEQuence:SELect \n
		Snippet: value: str = driver.sequence.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('SEQuence:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: SEQuence:SELect \n
		Snippet: driver.sequence.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'SEQuence:SELect {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SequenceType:
		"""SCPI: SEQuence:TYPE \n
		Snippet: value: enums.SequenceType = driver.sequence.get_type_py() \n
		Sets the sequence type. \n
			:return: type_py: PULSe | | WAVeform
		"""
		response = self._core.io.query_str('SEQuence:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SequenceType)

	def set_type_py(self, type_py: enums.SequenceType) -> None:
		"""SCPI: SEQuence:TYPE \n
		Snippet: driver.sequence.set_type_py(type_py = enums.SequenceType.PULSe) \n
		Sets the sequence type. \n
			:param type_py: PULSe | | WAVeform
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.SequenceType)
		self._core.io.write(f'SEQuence:TYPE {param}')

	def clone(self) -> 'Sequence':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Sequence(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
