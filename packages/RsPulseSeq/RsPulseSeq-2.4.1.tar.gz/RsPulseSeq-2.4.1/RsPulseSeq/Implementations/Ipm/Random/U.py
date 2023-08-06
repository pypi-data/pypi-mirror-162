from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class U:
	"""U commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("u", core, parent)

	def get_center(self) -> float:
		"""SCPI: IPM:RANDom:U:CENTer \n
		Snippet: value: float = driver.ipm.random.u.get_center() \n
		Sets the center parameter of the U distribution. \n
			:return: center: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:U:CENTer?')
		return Conversions.str_to_float(response)

	def set_center(self, center: float) -> None:
		"""SCPI: IPM:RANDom:U:CENTer \n
		Snippet: driver.ipm.random.u.set_center(center = 1.0) \n
		Sets the center parameter of the U distribution. \n
			:param center: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(center)
		self._core.io.write(f'IPM:RANDom:U:CENTer {param}')

	def get_range(self) -> float:
		"""SCPI: IPM:RANDom:U:RANGe \n
		Snippet: value: float = driver.ipm.random.u.get_range() \n
		Sets the range parameter of the U distribution. \n
			:return: range_py: float Range: 1e-09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:RANDom:U:RANGe?')
		return Conversions.str_to_float(response)

	def set_range(self, range_py: float) -> None:
		"""SCPI: IPM:RANDom:U:RANGe \n
		Snippet: driver.ipm.random.u.set_range(range_py = 1.0) \n
		Sets the range parameter of the U distribution. \n
			:param range_py: float Range: 1e-09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(range_py)
		self._core.io.write(f'IPM:RANDom:U:RANGe {param}')
