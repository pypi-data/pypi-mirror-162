from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Array:
	"""Array commands group definition. 16 total commands, 4 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("array", core, parent)

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
	def element(self):
		"""element commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_element'):
			from .Element import Element
			self._element = Element(self._core, self._cmd_group)
		return self._element

	def get_nx(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:NX \n
		Snippet: value: float = driver.antenna.model.array.get_nx() \n
		Sets the number of elements of the antenna array. \n
			:return: nx: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:NX?')
		return Conversions.str_to_float(response)

	def set_nx(self, nx: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:NX \n
		Snippet: driver.antenna.model.array.set_nx(nx = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nx: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nx)
		self._core.io.write(f'ANTenna:MODel:ARRay:NX {param}')

	def get_nz(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:NZ \n
		Snippet: value: float = driver.antenna.model.array.get_nz() \n
		Sets the number of elements of the antenna array. \n
			:return: nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:NZ?')
		return Conversions.str_to_float(response)

	def set_nz(self, nz: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:NZ \n
		Snippet: driver.antenna.model.array.set_nz(nz = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nz)
		self._core.io.write(f'ANTenna:MODel:ARRay:NZ {param}')

	def get_xdistance(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:XDIStance \n
		Snippet: value: float = driver.antenna.model.array.get_xdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: xdistance: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:XDIStance?')
		return Conversions.str_to_float(response)

	def set_xdistance(self, xdistance: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:XDIStance \n
		Snippet: driver.antenna.model.array.set_xdistance(xdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param xdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(xdistance)
		self._core.io.write(f'ANTenna:MODel:ARRay:XDIStance {param}')

	def get_zdistance(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:ZDIStance \n
		Snippet: value: float = driver.antenna.model.array.get_zdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: zdistance: float Range: 0.0001 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:ZDIStance?')
		return Conversions.str_to_float(response)

	def set_zdistance(self, zdistance: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:ZDIStance \n
		Snippet: driver.antenna.model.array.set_zdistance(zdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param zdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(zdistance)
		self._core.io.write(f'ANTenna:MODel:ARRay:ZDIStance {param}')

	def get_resolution(self) -> float:
		"""SCPI: ANTenna:MODel:ARRay:RESolution \n
		Snippet: value: float = driver.antenna.model.array.get_resolution() \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:return: resolution: float Range: 0.1 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:ARRay:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""SCPI: ANTenna:MODel:ARRay:RESolution \n
		Snippet: driver.antenna.model.array.set_resolution(resolution = 1.0) \n
		Sets a custom resolution for the antenna pattern simulation. \n
			:param resolution: float Range: 0.1 to 1
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ANTenna:MODel:ARRay:RESolution {param}')

	def clone(self) -> 'Array':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Array(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
