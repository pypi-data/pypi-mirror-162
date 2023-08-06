from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Am:
	"""Am commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("am", core, parent)

	def get_frequency(self) -> float:
		"""SCPI: PULSe:MOP:AM:FREQuency \n
		Snippet: value: float = driver.pulse.mop.am.get_frequency() \n
		Sets modulation frequency. \n
			:return: frequency: float Range: 0.001 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:AM:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: PULSe:MOP:AM:FREQuency \n
		Snippet: driver.pulse.mop.am.set_frequency(frequency = 1.0) \n
		Sets modulation frequency. \n
			:param frequency: float Range: 0.001 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'PULSe:MOP:AM:FREQuency {param}')

	def get_mdepth(self) -> float:
		"""SCPI: PULSe:MOP:AM:MDEPth \n
		Snippet: value: float = driver.pulse.mop.am.get_mdepth() \n
		Sets the modulation depth. \n
			:return: mdepth: float Range: 0 to 100, Unit: percent
		"""
		response = self._core.io.query_str('PULSe:MOP:AM:MDEPth?')
		return Conversions.str_to_float(response)

	def set_mdepth(self, mdepth: float) -> None:
		"""SCPI: PULSe:MOP:AM:MDEPth \n
		Snippet: driver.pulse.mop.am.set_mdepth(mdepth = 1.0) \n
		Sets the modulation depth. \n
			:param mdepth: float Range: 0 to 100, Unit: percent
		"""
		param = Conversions.decimal_value_to_str(mdepth)
		self._core.io.write(f'PULSe:MOP:AM:MDEPth {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.AmType:
		"""SCPI: PULSe:MOP:AM:TYPE \n
		Snippet: value: enums.AmType = driver.pulse.mop.am.get_type_py() \n
		Selects the modulation type. \n
			:return: type_py: STD| LSB| USB| SB
		"""
		response = self._core.io.query_str('PULSe:MOP:AM:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.AmType)

	def set_type_py(self, type_py: enums.AmType) -> None:
		"""SCPI: PULSe:MOP:AM:TYPE \n
		Snippet: driver.pulse.mop.am.set_type_py(type_py = enums.AmType.LSB) \n
		Selects the modulation type. \n
			:param type_py: STD| LSB| USB| SB
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.AmType)
		self._core.io.write(f'PULSe:MOP:AM:TYPE {param}')
