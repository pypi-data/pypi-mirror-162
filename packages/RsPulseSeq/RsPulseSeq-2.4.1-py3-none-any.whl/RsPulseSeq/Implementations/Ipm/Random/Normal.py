from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Normal:
	"""Normal commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("normal", core, parent)

	def get_limit(self) -> float:
		"""SCPI: IPM:RANDom:NORMal:LIMit \n
		Snippet: value: float = driver.ipm.random.normal.get_limit() \n
		Sets the limit parameter of the normal distribution function. \n
			:return: limit: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:NORMal:LIMit?')
		return Conversions.str_to_float(response)

	def set_limit(self, limit: float) -> None:
		"""SCPI: IPM:RANDom:NORMal:LIMit \n
		Snippet: driver.ipm.random.normal.set_limit(limit = 1.0) \n
		Sets the limit parameter of the normal distribution function. \n
			:param limit: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(limit)
		self._core.io.write(f'IPM:RANDom:NORMal:LIMit {param}')

	def get_mean(self) -> float:
		"""SCPI: IPM:RANDom:NORMal:MEAN \n
		Snippet: value: float = driver.ipm.random.normal.get_mean() \n
		Sets the mean parameter of the normal distribution function. \n
			:return: mean: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:NORMal:MEAN?')
		return Conversions.str_to_float(response)

	def set_mean(self, mean: float) -> None:
		"""SCPI: IPM:RANDom:NORMal:MEAN \n
		Snippet: driver.ipm.random.normal.set_mean(mean = 1.0) \n
		Sets the mean parameter of the normal distribution function. \n
			:param mean: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(mean)
		self._core.io.write(f'IPM:RANDom:NORMal:MEAN {param}')

	def get_std(self) -> float:
		"""SCPI: IPM:RANDom:NORMal:STD \n
		Snippet: value: float = driver.ipm.random.normal.get_std() \n
		Sets the standard deviation parameter of the normal distribution function. \n
			:return: std: float Range: 1e-09 to 1e+06
		"""
		response = self._core.io.query_str('IPM:RANDom:NORMal:STD?')
		return Conversions.str_to_float(response)

	def set_std(self, std: float) -> None:
		"""SCPI: IPM:RANDom:NORMal:STD \n
		Snippet: driver.ipm.random.normal.set_std(std = 1.0) \n
		Sets the standard deviation parameter of the normal distribution function. \n
			:param std: float Range: 1e-09 to 1e+06
		"""
		param = Conversions.decimal_value_to_str(std)
		self._core.io.write(f'IPM:RANDom:NORMal:STD {param}')
