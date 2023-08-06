from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Qam:
	"""Qam commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("qam", core, parent)

	def get_symbol_rate(self) -> float:
		"""SCPI: PULSe:MOP:QAM:SRATe \n
		Snippet: value: float = driver.pulse.mop.qam.get_symbol_rate() \n
		Sets the symbol rate of the modulated signal. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:QAM:SRATe?')
		return Conversions.str_to_float(response)

	def set_symbol_rate(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:QAM:SRATe \n
		Snippet: driver.pulse.mop.qam.set_symbol_rate(srate = 1.0) \n
		Sets the symbol rate of the modulated signal. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:QAM:SRATe {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.QamType:
		"""SCPI: PULSe:MOP:QAM:TYPE \n
		Snippet: value: enums.QamType = driver.pulse.mop.qam.get_type_py() \n
		Selects the QAM type. \n
			:return: type_py: Q16| Q32| Q64| Q128| Q256
		"""
		response = self._core.io.query_str('PULSe:MOP:QAM:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.QamType)

	def set_type_py(self, type_py: enums.QamType) -> None:
		"""SCPI: PULSe:MOP:QAM:TYPE \n
		Snippet: driver.pulse.mop.qam.set_type_py(type_py = enums.QamType.Q128) \n
		Selects the QAM type. \n
			:param type_py: Q16| Q32| Q64| Q128| Q256
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.QamType)
		self._core.io.write(f'PULSe:MOP:QAM:TYPE {param}')
