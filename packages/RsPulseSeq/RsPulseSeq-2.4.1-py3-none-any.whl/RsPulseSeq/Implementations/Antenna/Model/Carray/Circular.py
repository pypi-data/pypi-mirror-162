from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Circular:
	"""Circular commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("circular", core, parent)

	def get_distance(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:DISTance \n
		Snippet: value: float = driver.antenna.model.carray.circular.get_distance() \n
		Sets the spacing between the elements of the array antenna. \n
			:return: distance: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:CIRCular:DISTance?')
		return Conversions.str_to_float(response)

	def set_distance(self, distance: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:DISTance \n
		Snippet: driver.antenna.model.carray.circular.set_distance(distance = 1.0) \n
		Sets the spacing between the elements of the array antenna. \n
			:param distance: float Range: 0.0001 to 1
		"""
		param = Conversions.decimal_value_to_str(distance)
		self._core.io.write(f'ANTenna:MODel:CARRay:CIRCular:DISTance {param}')

	# noinspection PyTypeChecker
	def get_lattice(self) -> enums.Lattice:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:LATTice \n
		Snippet: value: enums.Lattice = driver.antenna.model.carray.circular.get_lattice() \n
		Sets the lattice. \n
			:return: lattice: RECTangular| TRIangular
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:CIRCular:LATTice?')
		return Conversions.str_to_scalar_enum(response, enums.Lattice)

	def set_lattice(self, lattice: enums.Lattice) -> None:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:LATTice \n
		Snippet: driver.antenna.model.carray.circular.set_lattice(lattice = enums.Lattice.RECTangular) \n
		Sets the lattice. \n
			:param lattice: RECTangular| TRIangular
		"""
		param = Conversions.enum_scalar_to_str(lattice, enums.Lattice)
		self._core.io.write(f'ANTenna:MODel:CARRay:CIRCular:LATTice {param}')

	def get_radius(self) -> float:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:RADius \n
		Snippet: value: float = driver.antenna.model.carray.circular.get_radius() \n
		Set the radius of the circular phased array antenna. \n
			:return: radius: float Range: 1 to 50
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:CIRCular:RADius?')
		return Conversions.str_to_float(response)

	def set_radius(self, radius: float) -> None:
		"""SCPI: ANTenna:MODel:CARRay:CIRCular:RADius \n
		Snippet: driver.antenna.model.carray.circular.set_radius(radius = 1.0) \n
		Set the radius of the circular phased array antenna. \n
			:param radius: float Range: 1 to 50
		"""
		param = Conversions.decimal_value_to_str(radius)
		self._core.io.write(f'ANTenna:MODel:CARRay:CIRCular:RADius {param}')
