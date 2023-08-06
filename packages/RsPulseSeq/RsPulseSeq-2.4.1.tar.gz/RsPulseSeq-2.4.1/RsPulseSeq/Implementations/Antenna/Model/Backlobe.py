from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Backlobe:
	"""Backlobe commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("backlobe", core, parent)

	def get_attenuation(self) -> float:
		"""SCPI: ANTenna:MODel:BACKlobe:ATTenuation \n
		Snippet: value: float = driver.antenna.model.backlobe.get_attenuation() \n
		Sets the attenuation of the back lobe. \n
			:return: attenuation: float Range: 0 to 100
		"""
		response = self._core.io.query_str('ANTenna:MODel:BACKlobe:ATTenuation?')
		return Conversions.str_to_float(response)

	def set_attenuation(self, attenuation: float) -> None:
		"""SCPI: ANTenna:MODel:BACKlobe:ATTenuation \n
		Snippet: driver.antenna.model.backlobe.set_attenuation(attenuation = 1.0) \n
		Sets the attenuation of the back lobe. \n
			:param attenuation: float Range: 0 to 100
		"""
		param = Conversions.decimal_value_to_str(attenuation)
		self._core.io.write(f'ANTenna:MODel:BACKlobe:ATTenuation {param}')

	def get_enable(self) -> bool:
		"""SCPI: ANTenna:MODel:BACKlobe:ENABle \n
		Snippet: value: bool = driver.antenna.model.backlobe.get_enable() \n
		Enables the simulation of a back lobe. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('ANTenna:MODel:BACKlobe:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: ANTenna:MODel:BACKlobe:ENABle \n
		Snippet: driver.antenna.model.backlobe.set_enable(enable = False) \n
		Enables the simulation of a back lobe. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'ANTenna:MODel:BACKlobe:ENABle {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.BlType:
		"""SCPI: ANTenna:MODel:BACKlobe:TYPE \n
		Snippet: value: enums.BlType = driver.antenna.model.backlobe.get_type_py() \n
		Sets the shape of the back lobe pattern. \n
			:return: type_py: MIRRor| OMNidirect
		"""
		response = self._core.io.query_str('ANTenna:MODel:BACKlobe:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.BlType)

	def set_type_py(self, type_py: enums.BlType) -> None:
		"""SCPI: ANTenna:MODel:BACKlobe:TYPE \n
		Snippet: driver.antenna.model.backlobe.set_type_py(type_py = enums.BlType.MIRRor) \n
		Sets the shape of the back lobe pattern. \n
			:param type_py: MIRRor| OMNidirect
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.BlType)
		self._core.io.write(f'ANTenna:MODel:BACKlobe:TYPE {param}')
