from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Ipm:
	"""Ipm commands group definition. 66 total commands, 9 Subgroups, 9 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ipm", core, parent)

	@property
	def binomial(self):
		"""binomial commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_binomial'):
			from .Binomial import Binomial
			self._binomial = Binomial(self._core, self._cmd_group)
		return self._binomial

	@property
	def listPy(self):
		"""listPy commands group. 2 Sub-classes, 4 commands."""
		if not hasattr(self, '_listPy'):
			from .ListPy import ListPy
			self._listPy = ListPy(self._core, self._cmd_group)
		return self._listPy

	@property
	def plugin(self):
		"""plugin commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_plugin'):
			from .Plugin import Plugin
			self._plugin = Plugin(self._core, self._cmd_group)
		return self._plugin

	@property
	def random(self):
		"""random commands group. 3 Sub-classes, 1 commands."""
		if not hasattr(self, '_random'):
			from .Random import Random
			self._random = Random(self._core, self._cmd_group)
		return self._random

	@property
	def rlist(self):
		"""rlist commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_rlist'):
			from .Rlist import Rlist
			self._rlist = Rlist(self._core, self._cmd_group)
		return self._rlist

	@property
	def rstep(self):
		"""rstep commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_rstep'):
			from .Rstep import Rstep
			self._rstep = Rstep(self._core, self._cmd_group)
		return self._rstep

	@property
	def shape(self):
		"""shape commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_shape'):
			from .Shape import Shape
			self._shape = Shape(self._core, self._cmd_group)
		return self._shape

	@property
	def step(self):
		"""step commands group. 0 Sub-classes, 6 commands."""
		if not hasattr(self, '_step'):
			from .Step import Step
			self._step = Step(self._core, self._cmd_group)
		return self._step

	@property
	def waveform(self):
		"""waveform commands group. 0 Sub-classes, 7 commands."""
		if not hasattr(self, '_waveform'):
			from .Waveform import Waveform
			self._waveform = Waveform(self._core, self._cmd_group)
		return self._waveform

	def get_catalog(self) -> str:
		"""SCPI: IPM:CATalog \n
		Snippet: value: str = driver.ipm.get_catalog() \n
		Queries the available repository elements in the database. \n
			:return: catalog: string
		"""
		response = self._core.io.query_str('IPM:CATalog?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: IPM:COMMent \n
		Snippet: value: str = driver.ipm.get_comment() \n
		Adds a description to the selected repository element. \n
			:return: comment: string
		"""
		response = self._core.io.query_str('IPM:COMMent?')
		return trim_str_response(response)

	def set_comment(self, comment: str) -> None:
		"""SCPI: IPM:COMMent \n
		Snippet: driver.ipm.set_comment(comment = '1') \n
		Adds a description to the selected repository element. \n
			:param comment: string
		"""
		param = Conversions.value_to_quoted_str(comment)
		self._core.io.write(f'IPM:COMMent {param}')

	def set_create(self, create: str) -> None:
		"""SCPI: IPM:CREate \n
		Snippet: driver.ipm.set_create(create = '1') \n
		Creates a repository element with the selected name. \n
			:param create: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(create)
		self._core.io.write(f'IPM:CREate {param}')

	def get_equation(self) -> str:
		"""SCPI: IPM:EQUation \n
		Snippet: value: str = driver.ipm.get_equation() \n
		Defines the IPM shape as a function. \n
			:return: equation: string
		"""
		response = self._core.io.query_str('IPM:EQUation?')
		return trim_str_response(response)

	def set_equation(self, equation: str) -> None:
		"""SCPI: IPM:EQUation \n
		Snippet: driver.ipm.set_equation(equation = '1') \n
		Defines the IPM shape as a function. \n
			:param equation: string
		"""
		param = Conversions.value_to_quoted_str(equation)
		self._core.io.write(f'IPM:EQUation {param}')

	def get_name(self) -> str:
		"""SCPI: IPM:NAME \n
		Snippet: value: str = driver.ipm.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('IPM:NAME?')
		return trim_str_response(response)

	def set_name(self, name: str) -> None:
		"""SCPI: IPM:NAME \n
		Snippet: driver.ipm.set_name(name = '1') \n
		Renames the selected repository element. \n
			:param name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		param = Conversions.value_to_quoted_str(name)
		self._core.io.write(f'IPM:NAME {param}')

	def set_remove(self, remove: str) -> None:
		"""SCPI: IPM:REMove \n
		Snippet: driver.ipm.set_remove(remove = '1') \n
		Removes the selected element from the workspace. The element must not reference any child elements. Remove the referenced
		elements first. \n
			:param remove: No help available
		"""
		param = Conversions.value_to_quoted_str(remove)
		self._core.io.write(f'IPM:REMove {param}')

	def get_select(self) -> str:
		"""SCPI: IPM:SELect \n
		Snippet: value: str = driver.ipm.get_select() \n
		Selects the repository element to which the subsequent commands apply. \n
			:return: select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		response = self._core.io.query_str('IPM:SELect?')
		return trim_str_response(response)

	def set_select(self, select: str) -> None:
		"""SCPI: IPM:SELect \n
		Snippet: driver.ipm.set_select(select = '1') \n
		Selects the repository element to which the subsequent commands apply. \n
			:param select: string Element name, as defined with the ...:CREate or ...:NAME command. To query the existing elements, use the ...:CATalog? command. For example, method RsPulseSeq.Repository.catalog.
		"""
		param = Conversions.value_to_quoted_str(select)
		self._core.io.write(f'IPM:SELect {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.IpmType:
		"""SCPI: IPM:TYPE \n
		Snippet: value: enums.IpmType = driver.ipm.get_type_py() \n
		Sets the shape of the profile. \n
			:return: type_py: STEPs| WAVeform| RLISt| LIST| SHAPe| RANDom| EQUation| PLUGin| RSTep| BINomial
		"""
		response = self._core.io.query_str('IPM:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.IpmType)

	def set_type_py(self, type_py: enums.IpmType) -> None:
		"""SCPI: IPM:TYPE \n
		Snippet: driver.ipm.set_type_py(type_py = enums.IpmType.BINomial) \n
		Sets the shape of the profile. \n
			:param type_py: STEPs| WAVeform| RLISt| LIST| SHAPe| RANDom| EQUation| PLUGin| RSTep| BINomial
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.IpmType)
		self._core.io.write(f'IPM:TYPE {param}')

	# noinspection PyTypeChecker
	def get_unit(self) -> enums.Units:
		"""SCPI: IPM:UNIT \n
		Snippet: value: enums.Units = driver.ipm.get_unit() \n
		Sets the units of the profile. \n
			:return: unit: NONE| SEConds| HERTz| DB| DEGRees| PERCent
		"""
		response = self._core.io.query_str('IPM:UNIT?')
		return Conversions.str_to_scalar_enum(response, enums.Units)

	def set_unit(self, unit: enums.Units) -> None:
		"""SCPI: IPM:UNIT \n
		Snippet: driver.ipm.set_unit(unit = enums.Units.DB) \n
		Sets the units of the profile. \n
			:param unit: NONE| SEConds| HERTz| DB| DEGRees| PERCent
		"""
		param = Conversions.enum_scalar_to_str(unit, enums.Units)
		self._core.io.write(f'IPM:UNIT {param}')

	def clone(self) -> 'Ipm':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Ipm(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
