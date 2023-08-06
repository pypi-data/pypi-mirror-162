from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Poly:
	"""Poly commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("poly", core, parent)

	def get_length(self) -> float:
		"""SCPI: PULSe:MOP:POLY:LENGth \n
		Snippet: value: float = driver.pulse.mop.poly.get_length() \n
		Sets the polyphase length (code order) . \n
			:return: length: integer Range: 1 to 100
		"""
		response = self._core.io.query_str('PULSe:MOP:POLY:LENGth?')
		return Conversions.str_to_float(response)

	def set_length(self, length: float) -> None:
		"""SCPI: PULSe:MOP:POLY:LENGth \n
		Snippet: driver.pulse.mop.poly.set_length(length = 1.0) \n
		Sets the polyphase length (code order) . \n
			:param length: integer Range: 1 to 100
		"""
		param = Conversions.decimal_value_to_str(length)
		self._core.io.write(f'PULSe:MOP:POLY:LENGth {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.PolynomType:
		"""SCPI: PULSe:MOP:POLY:TYPE \n
		Snippet: value: enums.PolynomType = driver.pulse.mop.poly.get_type_py() \n
		Selects the modulation type. \n
			:return: type_py: FRANk| P1| P2| P3| P4
		"""
		response = self._core.io.query_str('PULSe:MOP:POLY:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PolynomType)

	def set_type_py(self, type_py: enums.PolynomType) -> None:
		"""SCPI: PULSe:MOP:POLY:TYPE \n
		Snippet: driver.pulse.mop.poly.set_type_py(type_py = enums.PolynomType.FRANk) \n
		Selects the modulation type. \n
			:param type_py: FRANk| P1| P2| P3| P4
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.PolynomType)
		self._core.io.write(f'PULSe:MOP:POLY:TYPE {param}')
