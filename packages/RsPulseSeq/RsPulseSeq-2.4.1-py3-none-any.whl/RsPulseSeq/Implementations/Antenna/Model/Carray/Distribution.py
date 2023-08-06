from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Distribution:
	"""Distribution commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("distribution", core, parent)

	def get_type_py(self) -> bool:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:TYPE \n
		Snippet: value: bool = driver.antenna.model.carray.distribution.get_type_py() \n
		No command help available \n
			:return: type_py: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:DISTribution:TYPE?')
		return Conversions.str_to_bool(response)

	def set_type_py(self, type_py: bool) -> None:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:TYPE \n
		Snippet: driver.antenna.model.carray.distribution.set_type_py(type_py = False) \n
		No command help available \n
			:param type_py: No help available
		"""
		param = Conversions.bool_to_str(type_py)
		self._core.io.write(f'ANTenna:MODel:CARRay:DISTribution:TYPE {param}')

	# noinspection PyTypeChecker
	def get_x(self) -> enums.AntennaModelArray:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:X \n
		Snippet: value: enums.AntennaModelArray = driver.antenna.model.carray.distribution.get_x() \n
		No command help available \n
			:return: x: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:DISTribution:X?')
		return Conversions.str_to_scalar_enum(response, enums.AntennaModelArray)

	def set_x(self, x: enums.AntennaModelArray) -> None:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:X \n
		Snippet: driver.antenna.model.carray.distribution.set_x(x = enums.AntennaModelArray.COSine) \n
		No command help available \n
			:param x: No help available
		"""
		param = Conversions.enum_scalar_to_str(x, enums.AntennaModelArray)
		self._core.io.write(f'ANTenna:MODel:CARRay:DISTribution:X {param}')

	# noinspection PyTypeChecker
	def get_z(self) -> enums.AntennaModelArray:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:Z \n
		Snippet: value: enums.AntennaModelArray = driver.antenna.model.carray.distribution.get_z() \n
		No command help available \n
			:return: z: No help available
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:DISTribution:Z?')
		return Conversions.str_to_scalar_enum(response, enums.AntennaModelArray)

	def set_z(self, z: enums.AntennaModelArray) -> None:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution:Z \n
		Snippet: driver.antenna.model.carray.distribution.set_z(z = enums.AntennaModelArray.COSine) \n
		No command help available \n
			:param z: No help available
		"""
		param = Conversions.enum_scalar_to_str(z, enums.AntennaModelArray)
		self._core.io.write(f'ANTenna:MODel:CARRay:DISTribution:Z {param}')

	# noinspection PyTypeChecker
	def get_value(self) -> enums.AntennaModelArray:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution \n
		Snippet: value: enums.AntennaModelArray = driver.antenna.model.carray.distribution.get_value() \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:return: distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		response = self._core.io.query_str('ANTenna:MODel:CARRay:DISTribution?')
		return Conversions.str_to_scalar_enum(response, enums.AntennaModelArray)

	def set_value(self, distribution: enums.AntennaModelArray) -> None:
		"""SCPI: ANTenna:MODel:CARRay:DISTribution \n
		Snippet: driver.antenna.model.carray.distribution.set_value(distribution = enums.AntennaModelArray.COSine) \n
		Sets the aperture distribution of the Planar Phased Array antenna. \n
			:param distribution: UNIForm| PARabolic| COSine| CSQuared| COSN| TRIangular| HAMMing| HANN
		"""
		param = Conversions.enum_scalar_to_str(distribution, enums.AntennaModelArray)
		self._core.io.write(f'ANTenna:MODel:CARRay:DISTribution {param}')
