from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Dsrc:
	"""Dsrc commands group definition. 17 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dsrc", core, parent)

	@property
	def item(self):
		"""item commands group. 2 Sub-classes, 6 commands."""
		if not hasattr(self, '_item'):
			from .Item import Item
			self._item = Item(self._core, self._cmd_group)
		return self._item

	def get_catalog(self) -> str:
		"""SCPI: DSRC:CATalog \n
		Snippet: value: str = driver.dsrc.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('DSRC:CATalog?')
		return trim_str_response(response)

	def clear(self) -> None:
		"""SCPI: DSRC:CLEar \n
		Snippet: driver.dsrc.clear() \n
		Deletes all items from the list or the table. \n
		"""
		self._core.io.write(f'DSRC:CLEar')

	def clear_with_opc(self, opc_timeout_ms: int = -1) -> None:
		"""SCPI: DSRC:CLEar \n
		Snippet: driver.dsrc.clear_with_opc() \n
		Deletes all items from the list or the table. \n
		Same as clear, but waits for the operation to complete before continuing further. Use the RsPulseSeq.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DSRC:CLEar', opc_timeout_ms)

	def get_comment(self) -> str:
		"""SCPI: DSRC:COMMent \n
		Snippet: value: str = driver.dsrc.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('DSRC:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: DSRC:COMMent \n
		Snippet: driver.dsrc.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'DSRC:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: DSRC:CREate \n
		Snippet: driver.dsrc.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'DSRC:CREate {param}')

	def get_name(self) -> str:
		"""SCPI: DSRC:NAME \n
		Snippet: value: str = driver.dsrc.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('DSRC:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: DSRC:NAME \n
		Snippet: driver.dsrc.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'DSRC:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: DSRC:REMove \n
		Snippet: driver.dsrc.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'DSRC:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: DSRC:SELect \n
		Snippet: value: str = driver.dsrc.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('DSRC:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: DSRC:SELect \n
		Snippet: driver.dsrc.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'DSRC:SELect {param}')

	def clone(self) -> 'Dsrc':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Dsrc(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
