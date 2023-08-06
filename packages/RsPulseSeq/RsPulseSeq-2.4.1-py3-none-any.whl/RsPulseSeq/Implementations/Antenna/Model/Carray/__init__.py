from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Carray:
	"""Carray commands group definition. 25 total commands, 8 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("carray", core, parent)

	@property
	def cosn(self):
		"""cosn commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_cosn'):
			from .Cosn import Cosn
			self._cosn = Cosn(self._core, self._cmd_group)
		return self._cosn

	@property
	def distribution(self):
		"""distribution commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_distribution'):
			from .Distribution import Distribution
			self._distribution = Distribution(self._core, self._cmd_group)
		return self._distribution

	@property
	def pedestal(self):
		"""pedestal commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_pedestal'):
			from .Pedestal import Pedestal
			self._pedestal = Pedestal(self._core, self._cmd_group)
		return self._pedestal

	@property
	def circular(self):
		"""circular commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_circular'):
			from .Circular import Circular
			self._circular = Circular(self._core, self._cmd_group)
		return self._circular

	@property
	def element(self):
		"""element commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_element'):
			from .Element import Element
			self._element = Element(self._core, self._cmd_group)
		return self._element

	@property
	def hexagonal(self):
		"""hexagonal commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_hexagonal'):
			from .Hexagonal import Hexagonal
			self._hexagonal = Hexagonal(self._core, self._cmd_group)
		return self._hexagonal

	@property
	def linear(self):
		"""linear commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_linear'):
			from .Linear import Linear
			self._linear = Linear(self._core, self._cmd_group)
		return self._linear

	@property
	def rectangular(self):
		"""rectangular commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_rectangular'):
			from .Rectangular import Rectangular
			self._rectangular = Rectangular(self._core, self._cmd_group)
		return self._rectangular

	# noinspection PyTypeChecker
	def get_geometry(self) -> enums.Geometry:
		"""SCPI: ANTenna:MODel:CARRay:GEOMetry \n
		Snippet: value: enums.Geometry = driver.antenna.model.carray.get_geometry() \n
		Sets the geometry of the custom phased array antenna. \n
			:return: geometry: RECTangular| LINear| HEXagonal| CIRCular
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:GEOMetry?')
		return Conversions.str_to_scalar_enum(response, enums.Geometry)

	def set_geometry(self, geometry: enums.Geometry) -> None:
		"""SCPI: ANTenna:MODel:CARRay:GEOMetry \n
		Snippet: driver.antenna.model.carray.set_geometry(geometry = enums.Geometry.CIRCular) \n
		Sets the geometry of the custom phased array antenna. \n
			:param geometry: RECTangular| LINear| HEXagonal| CIRCular
		"""
		param = Conversions.enum_scalar_to_str(geometry, enums.Geometry)
		self._core.io.write(f'ANTenna:MODel:CARRay:GEOMetry {param}')

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:RESolution \n
		Snippet: value: float = driver.antenna.model.carray.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RESolution \n
		Snippet: driver.antenna.model.carray.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:CARRay:RESolution {param}')

	def clone(self) -> 'Carray':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Carray(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
