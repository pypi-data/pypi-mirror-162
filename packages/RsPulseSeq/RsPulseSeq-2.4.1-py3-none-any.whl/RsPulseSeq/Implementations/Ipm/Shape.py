from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Shape:
	"""Shape commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("shape", core, parent)

	# noinspection PyTypeChecker
	def get_base(self) -> enums.BaseDomain:
		"""SCPI: IPM:SHAPe:BASE \n
		Snippet: value: enums.BaseDomain = driver.ipm.shape.get_base() \n
		Defines the way the list items are processed. \n
			:return: base: PULSe| TIME
		"""
		response = self._core.io.query_str('IPM:SHAPe:BASE?')
		return Conversions.str_to_scalar_enum(response, enums.BaseDomain)

	def set_base(self, base: enums.BaseDomain) -> None:
		"""SCPI: IPM:SHAPe:BASE \n
		Snippet: driver.ipm.shape.set_base(base = enums.BaseDomain.PULSe) \n
		Defines the way the list items are processed. \n
			:param base: PULSe| TIME
		"""
		param = Conversions.enum_scalar_to_str(base, enums.BaseDomain)
		self._core.io.write(f'IPM:SHAPe:BASE {param}')

	def get_count(self) -> float:
		"""SCPI: IPM:SHAPe:COUNt \n
		Snippet: value: float = driver.ipm.shape.get_count() \n
		Sets the number of pulses for that the data from the list is used. \n
			:return: count: integer Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('IPM:SHAPe:COUNt?')
		return Conversions.str_to_float(response)

	def set_count(self, count: float) -> None:
		"""SCPI: IPM:SHAPe:COUNt \n
		Snippet: driver.ipm.shape.set_count(count = 1.0) \n
		Sets the number of pulses for that the data from the list is used. \n
			:param count: integer Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(count)
		self._core.io.write(f'IPM:SHAPe:COUNt {param}')

	# noinspection PyTypeChecker
	def get_interpol(self) -> enums.Interpolation:
		"""SCPI: IPM:SHAPe:INTerpol \n
		Snippet: value: enums.Interpolation = driver.ipm.shape.get_interpol() \n
		Enables a linear transition between the increments. \n
			:return: interpol: LINear| NONE
		"""
		response = self._core.io.query_str('IPM:SHAPe:INTerpol?')
		return Conversions.str_to_scalar_enum(response, enums.Interpolation)

	def set_interpol(self, interpol: enums.Interpolation) -> None:
		"""SCPI: IPM:SHAPe:INTerpol \n
		Snippet: driver.ipm.shape.set_interpol(interpol = enums.Interpolation.LINear) \n
		Enables a linear transition between the increments. \n
			:param interpol: LINear| NONE
		"""
		param = Conversions.enum_scalar_to_str(interpol, enums.Interpolation)
		self._core.io.write(f'IPM:SHAPe:INTerpol {param}')

	def get_period(self) -> float:
		"""SCPI: IPM:SHAPe:PERiod \n
		Snippet: value: float = driver.ipm.shape.get_period() \n
		Sets the period of time over that the list items are equally distributed. \n
			:return: period: float Range: 1e-09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:SHAPe:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: IPM:SHAPe:PERiod \n
		Snippet: driver.ipm.shape.set_period(period = 1.0) \n
		Sets the period of time over that the list items are equally distributed. \n
			:param period: float Range: 1e-09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'IPM:SHAPe:PERiod {param}')
