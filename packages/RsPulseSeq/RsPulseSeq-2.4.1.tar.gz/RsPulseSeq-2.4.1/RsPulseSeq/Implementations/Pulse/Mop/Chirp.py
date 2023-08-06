from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Chirp:
	"""Chirp commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("chirp", core, parent)

	def get_deviation(self) -> float:
		"""SCPI: PULSe:MOP:CHIRp:DEViation \n
		Snippet: value: float = driver.pulse.mop.chirp.get_deviation() \n
		Sets the modulation deviation. \n
			:return: deviation: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:CHIRp:DEViation?')
		return Conversions.str_to_float(response)

	def set_deviation(self, deviation: float) -> None:
		"""SCPI: PULSe:MOP:CHIRp:DEViation \n
		Snippet: driver.pulse.mop.chirp.set_deviation(deviation = 1.0) \n
		Sets the modulation deviation. \n
			:param deviation: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(deviation)
		self._core.io.write(f'PULSe:MOP:CHIRp:DEViation {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ChirpType:
		"""SCPI: PULSe:MOP:CHIRp:TYPE \n
		Snippet: value: enums.ChirpType = driver.pulse.mop.chirp.get_type_py() \n
		Selects the modulation type. \n
			:return: type_py: UP| DOWN| SINE| TRIangular| PIECewise
		"""
		response = self._core.io.query_str('PULSe:MOP:CHIRp:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ChirpType)

	def set_type_py(self, type_py: enums.ChirpType) -> None:
		"""SCPI: PULSe:MOP:CHIRp:TYPE \n
		Snippet: driver.pulse.mop.chirp.set_type_py(type_py = enums.ChirpType.DOWN) \n
		Selects the modulation type. \n
			:param type_py: UP| DOWN| SINE| TRIangular| PIECewise
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.ChirpType)
		self._core.io.write(f'PULSe:MOP:CHIRp:TYPE {param}')
