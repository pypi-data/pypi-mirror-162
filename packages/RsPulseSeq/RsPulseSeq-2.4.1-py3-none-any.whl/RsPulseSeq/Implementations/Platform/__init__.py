from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Platform:
	"""Platform commands group definition. 31 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("platform", core, parent)

	@property
	def emitter(self):
		"""emitter commands group. 3 Sub-classes, 15 commands."""
		if not hasattr(self, '_emitter'):
			from .Emitter import Emitter
			self._emitter = Emitter(self._core, self._cmd_group)
		return self._emitter

	def get_id(self) -> float:
		"""SCPI: PLATform:ID \n
		Snippet: value: float = driver.platform.get_id() \n
		Platform identifier. \n
			:return: idn: float Range: 1 to 65536
		"""
		response = self._core.io.query_str('PLATform:ID?')
		return Conversions.str_to_float(response)

	def set_id(self, idn: float) -> None:
		"""SCPI: PLATform:ID \n
		Snippet: driver.platform.set_id(idn = 1.0) \n
		Platform identifier. \n
			:param idn: float Range: 1 to 65536
		"""
		param = Conversions.decimal_value_to_str(idn)
		self._core.io.write(f'PLATform:ID {param}')

	def get_catalog(self) -> str:
		"""SCPI: PLATform:CATalog \n
		Snippet: value: str = driver.platform.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('PLATform:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: PLATform:COMMent \n
		Snippet: value: str = driver.platform.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('PLATform:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: PLATform:COMMent \n
		Snippet: driver.platform.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'PLATform:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: PLATform:CREate \n
		Snippet: driver.platform.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'PLATform:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: PLATform:NAME \n
		Snippet: value: str = driver.platform.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('PLATform:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: PLATform:NAME \n
		Snippet: driver.platform.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'PLATform:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: PLATform:REMove \n
		Snippet: driver.platform.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'PLATform:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: PLATform:SELect \n
		Snippet: value: str = driver.platform.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('PLATform:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: PLATform:SELect \n
		Snippet: driver.platform.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'PLATform:SELect {param}')

	def clone(self) -> 'Platform':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Platform(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
