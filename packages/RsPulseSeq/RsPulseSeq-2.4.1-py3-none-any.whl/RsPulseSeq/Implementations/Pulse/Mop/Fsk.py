from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fsk:
	"""Fsk commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fsk", core, parent)

	def get_deviation(self) -> float:
		"""SCPI: PULSe:MOP:FSK:DEViation \n
		Snippet: value: float = driver.pulse.mop.fsk.get_deviation() \n
		Sets the modulation deviation. \n
			:return: deviation: float Range: 0.001 to 1e+09, Unit: Hz
		"""
		response = self._core.io.query_str('PULSe:MOP:FSK:DEViation?')
		return Conversions.str_to_float(response)

	def set_deviation(self, deviation: float) -> None:
		"""SCPI: PULSe:MOP:FSK:DEViation \n
		Snippet: driver.pulse.mop.fsk.set_deviation(deviation = 1.0) \n
		Sets the modulation deviation. \n
			:param deviation: float Range: 0.001 to 1e+09, Unit: Hz
		"""
		param = Conversions.decimal_value_to_str(deviation)
		self._core.io.write(f'PULSe:MOP:FSK:DEViation {param}')

	def get_invert(self) -> bool:
		"""SCPI: PULSe:MOP:FSK:INVert \n
		Snippet: value: bool = driver.pulse.mop.fsk.get_invert() \n
		Inverts the modulation. \n
			:return: invert: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:FSK:INVert?')
		return Conversions.str_to_bool(response)

	def set_invert(self, invert: bool) -> None:
		"""SCPI: PULSe:MOP:FSK:INVert \n
		Snippet: driver.pulse.mop.fsk.set_invert(invert = False) \n
		Inverts the modulation. \n
			:param invert: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(invert)
		self._core.io.write(f'PULSe:MOP:FSK:INVert {param}')

	def get_symbol_rate(self) -> float:
		"""SCPI: PULSe:MOP:FSK:SRATe \n
		Snippet: value: float = driver.pulse.mop.fsk.get_symbol_rate() \n
		Sets the symbol rate of the modulated signal. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:FSK:SRATe?')
		return Conversions.str_to_float(response)

	def set_symbol_rate(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:FSK:SRATe \n
		Snippet: driver.pulse.mop.fsk.set_symbol_rate(srate = 1.0) \n
		Sets the symbol rate of the modulated signal. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:FSK:SRATe {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.FskType:
		"""SCPI: PULSe:MOP:FSK:TYPE \n
		Snippet: value: enums.FskType = driver.pulse.mop.fsk.get_type_py() \n
		Selects the FSK modulation type. \n
			:return: type_py: FS2| FS4| FS8| FS16| FS32| FS64
		"""
		response = self._core.io.query_str('PULSe:MOP:FSK:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.FskType)

	def set_type_py(self, type_py: enums.FskType) -> None:
		"""SCPI: PULSe:MOP:FSK:TYPE \n
		Snippet: driver.pulse.mop.fsk.set_type_py(type_py = enums.FskType.FS16) \n
		Selects the FSK modulation type. \n
			:param type_py: FS2| FS4| FS8| FS16| FS32| FS64
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.FskType)
		self._core.io.write(f'PULSe:MOP:FSK:TYPE {param}')
