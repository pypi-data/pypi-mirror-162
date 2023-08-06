from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Binomial:
	"""Binomial commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("binomial", core, parent)

	def get_pval_1(self) -> float:
		"""SCPI: IPM:BINomial:PVAL1 \n
		Snippet: value: float = driver.ipm.binomial.get_pval_1() \n
		Sets the probability of occurrence of value 1 in the binomial distribution function. \n
			:return: pval_1: float Range: 0 to 100, Unit: PCT
		"""
		response = self._core.io.query_str('IPM:BINomial:PVAL1?')
		return Conversions.str_to_float(response)

	def set_pval_1(self, pval_1: float) -> None:
		"""SCPI: IPM:BINomial:PVAL1 \n
		Snippet: driver.ipm.binomial.set_pval_1(pval_1 = 1.0) \n
		Sets the probability of occurrence of value 1 in the binomial distribution function. \n
			:param pval_1: float Range: 0 to 100, Unit: PCT
		"""
		param = Conversions.decimal_value_to_str(pval_1)
		self._core.io.write(f'IPM:BINomial:PVAL1 {param}')

	def get_val_1(self) -> float:
		"""SCPI: IPM:BINomial:VAL1 \n
		Snippet: value: float = driver.ipm.binomial.get_val_1() \n
		Sets the values of the binomial distribution function. \n
			:return: val_1: No help available
		"""
		response = self._core.io.query_str('IPM:BINomial:VAL1?')
		return Conversions.str_to_float(response)

	def set_val_1(self, val_1: float) -> None:
		"""SCPI: IPM:BINomial:VAL1 \n
		Snippet: driver.ipm.binomial.set_val_1(val_1 = 1.0) \n
		Sets the values of the binomial distribution function. \n
			:param val_1: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(val_1)
		self._core.io.write(f'IPM:BINomial:VAL1 {param}')

	def get_val_2(self) -> float:
		"""SCPI: IPM:BINomial:VAL2 \n
		Snippet: value: float = driver.ipm.binomial.get_val_2() \n
		Sets the values of the binomial distribution function. \n
			:return: val_2: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:BINomial:VAL2?')
		return Conversions.str_to_float(response)

	def set_val_2(self, val_2: float) -> None:
		"""SCPI: IPM:BINomial:VAL2 \n
		Snippet: driver.ipm.binomial.set_val_2(val_2 = 1.0) \n
		Sets the values of the binomial distribution function. \n
			:param val_2: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(val_2)
		self._core.io.write(f'IPM:BINomial:VAL2 {param}')
