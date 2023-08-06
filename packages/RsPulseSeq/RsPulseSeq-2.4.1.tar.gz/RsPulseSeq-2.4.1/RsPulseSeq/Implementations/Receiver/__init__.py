from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Receiver:
	"""Receiver commands group definition. 24 total commands, 1 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("receiver", core, parent)

	@property
	def antenna(self):
		"""antenna commands group. 3 Sub-classes, 8 commands."""
		if not hasattr(self, '_antenna'):
			from .Antenna import Antenna
			self._antenna = Antenna(self._core, self._cmd_group)
		return self._antenna

	def get_catalog(self) -> str:
		"""SCPI: RECeiver:CATalog \n
		Snippet: value: str = driver.receiver.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('RECeiver:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: RECeiver:COMMent \n
		Snippet: value: str = driver.receiver.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('RECeiver:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: RECeiver:COMMent \n
		Snippet: driver.receiver.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'RECeiver:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: RECeiver:CREate \n
		Snippet: driver.receiver.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'RECeiver:CREate {param}')

	# noinspection PyTypeChecker
	def get_model(self) -> enums.RecModel:
		"""SCPI: RECeiver:MODel \n
		Snippet: value: enums.RecModel = driver.receiver.get_model() \n
		Sets the receiver model. \n
			:return: model: INTerfero| TDOA For details, see 'Model'. INTerfero Interferometer TDOA Time difference of arrival
		"""
		response = self._core.io.query_str('RECeiver:MODel?')
		return Conversions.str_to_scalar_enum(response, enums.RecModel)

	def set_model(self, model: enums.RecModel) -> None:
		"""SCPI: RECeiver:MODel \n
		Snippet: driver.receiver.set_model(model = enums.RecModel.INTerfero) \n
		Sets the receiver model. \n
			:param model: INTerfero| TDOA For details, see 'Model'. INTerfero Interferometer TDOA Time difference of arrival
		"""
		param = Conversions.enum_scalar_to_str(model, enums.RecModel)
		self._core.io.write(f'RECeiver:MODel {param}')

	def get_name(self) -> str:
		"""SCPI: RECeiver:NAME \n
		Snippet: value: str = driver.receiver.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('RECeiver:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: RECeiver:NAME \n
		Snippet: driver.receiver.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'RECeiver:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: RECeiver:REMove \n
		Snippet: driver.receiver.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'RECeiver:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: RECeiver:SELect \n
		Snippet: value: str = driver.receiver.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('RECeiver:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: RECeiver:SELect \n
		Snippet: driver.receiver.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'RECeiver:SELect {param}')

	def clone(self) -> 'Receiver':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Receiver(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
