from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Emitter:
	"""Emitter commands group definition. 30 total commands, 1 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("emitter", core, parent)

	@property
	def mode(self):
		"""mode commands group. 4 Sub-classes, 6 commands."""
		if not hasattr(self, '_mode'):
			from .Mode import Mode
			self._mode = Mode(self._core, self._cmd_group)
		return self._mode

	def get_catalog(self) -> str:
		"""SCPI: EMITter:CATalog \n
		Snippet: value: str = driver.emitter.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('EMITter:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: EMITter:COMMent \n
		Snippet: value: str = driver.emitter.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('EMITter:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: EMITter:COMMent \n
		Snippet: driver.emitter.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'EMITter:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: EMITter:CREate \n
		Snippet: driver.emitter.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'EMITter:CREate {param}')

	def get_eirp(self) -> float:
		"""SCPI: EMITter:EIRP \n
		Snippet: value: float = driver.emitter.get_eirp() \n
		Sets the EIRP of the emitter. \n
			:return: eirp: float Range: -100 to 200, Unit: dBW
		"""
		response = self._core.io.query_str('EMITter:EIRP?')
		return Conversions.str_to_float(response)

	def set_eirp(self, eirp: float) -> None:
		"""SCPI: EMITter:EIRP \n
		Snippet: driver.emitter.set_eirp(eirp = 1.0) \n
		Sets the EIRP of the emitter. \n
			:param eirp: float Range: -100 to 200, Unit: dBW
		"""
		param = Conversions.decimal_value_to_str(eirp)
		self._core.io.write(f'EMITter:EIRP {param}')

	def get_frequency(self) -> float:
		"""SCPI: EMITter:FREQuency \n
		Snippet: value: float = driver.emitter.get_frequency() \n
		Sets the operating frequency. \n
			:return: frequency: float Range: 1000 to 4.4e+10, Unit: Hz
		"""
		response = self._core.io.query_str('EMITter:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: EMITter:FREQuency \n
		Snippet: driver.emitter.set_frequency(frequency = 1.0) \n
		Sets the operating frequency. \n
			:param frequency: float Range: 1000 to 4.4e+10, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'EMITter:FREQuency {param}')

	def get_name(self) -> str:
		"""SCPI: EMITter:NAME \n
		Snippet: value: str = driver.emitter.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('EMITter:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: EMITter:NAME \n
		Snippet: driver.emitter.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'EMITter:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: EMITter:REMove \n
		Snippet: driver.emitter.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'EMITter:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: EMITter:SELect \n
		Snippet: value: str = driver.emitter.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('EMITter:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: EMITter:SELect \n
		Snippet: driver.emitter.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'EMITter:SELect {param}')

	def clone(self) -> 'Emitter':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Emitter(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
