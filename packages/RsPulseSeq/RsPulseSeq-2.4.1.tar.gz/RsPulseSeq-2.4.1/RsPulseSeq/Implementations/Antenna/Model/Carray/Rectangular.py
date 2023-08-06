from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Rectangular:
	"""Rectangular commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rectangular", core, parent)

	# noinspection PyTypeChecker
	def get_lattice(self) -> enums.Lattice:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:LATTice \n
		Snippet: value: enums.Lattice = driver.antenna.model.carray.rectangular.get_lattice() \n
		Sets the lattice. \n
			:return: lattice: RECTangular| TRIangular
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RECTangular:LATTice?')
		return Conversions.str_to_scalar_enum(response, enums.Lattice)

	def set_lattice(self, lattice: enums.Lattice) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:LATTice \n
		Snippet: driver.antenna.model.carray.rectangular.set_lattice(lattice = enums.Lattice.RECTangular) \n
		Sets the lattice. \n
			:param lattice: RECTangular| TRIangular
		"""
		param = Conversions.enum_scalar_to_str(lattice, enums.Lattice)
		self._core.io.write(f'ANTenna:MODel:CARRay:RECTangular:LATTice {param}')

	def get_nx(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:NX \n
		Snippet: value: float = driver.antenna.model.carray.rectangular.get_nx() \n
		Sets the number of elements of the antenna array. \n
			:return: nx: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RECTangular:NX?')
		return Conversions.str_to_float(response)

	def set_nx(self, nx: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:NX \n
		Snippet: driver.antenna.model.carray.rectangular.set_nx(nx = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nx: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nx)
		self._core.io.write(f'ANTenna:MODel:CARRay:RECTangular:NX {param}')

	def get_nz(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:NZ \n
		Snippet: value: float = driver.antenna.model.carray.rectangular.get_nz() \n
		Sets the number of elements of the antenna array. \n
			:return: nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RECTangular:NZ?')
		return Conversions.str_to_float(response)

	def set_nz(self, nz: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:NZ \n
		Snippet: driver.antenna.model.carray.rectangular.set_nz(nz = 1.0) \n
		Sets the number of elements of the antenna array. \n
			:param nz: float Range: 2 to 1000 (planar phased array; linear phase array) , 100 (rectangular phase array) , 50 (hexagonal phase array)
		"""
		param = Conversions.decimal_value_to_str(nz)
		self._core.io.write(f'ANTenna:MODel:CARRay:RECTangular:NZ {param}')

	def get_xdistance(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:XDIStance \n
		Snippet: value: float = driver.antenna.model.carray.rectangular.get_xdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: xdistance: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RECTangular:XDIStance?')
		return Conversions.str_to_float(response)

	def set_xdistance(self, xdistance: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:XDIStance \n
		Snippet: driver.antenna.model.carray.rectangular.set_xdistance(xdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param xdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(xdistance)
		self._core.io.write(f'ANTenna:MODel:CARRay:RECTangular:XDIStance {param}')

	def get_zdistance(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:ZDIStance \n
		Snippet: value: float = driver.antenna.model.carray.rectangular.get_zdistance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: zdistance: float Range: 0.0001 to 1
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:RECTangular:ZDIStance?')
		return Conversions.str_to_float(response)

	def set_zdistance(self, zdistance: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:RECTangular:ZDIStance \n
		Snippet: driver.antenna.model.carray.rectangular.set_zdistance(zdistance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param zdistance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(zdistance)
		self._core.io.write(f'ANTenna:MODel:CARRay:RECTangular:ZDIStance {param}')
