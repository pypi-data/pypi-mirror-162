from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Waveform:
	"""Waveform commands group definition. 7 total commands, 0 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("waveform", core, parent)

	# noinspection PyTypeChecker
	def get_base(self) -> enums.BaseDomain:
		"""SCPI: IPM:WAVeform:BASE \n
		Snippet: value: enums.BaseDomain = driver.ipm.waveform.get_base() \n
		Defines how the waveform period is defined, as a time duration or as a number of pulses. \n
			:return: base: PULSe| TIME
		"""
		response = self._core.io.query_str('IPM:WAVeform:BASE?')
		return Conversions.str_to_scalar_enum(response, enums.BaseDomain)

	def set_base(self, base: enums.BaseDomain) -> None:
		"""SCPI: IPM:WAVeform:BASE \n
		Snippet: driver.ipm.waveform.set_base(base = enums.BaseDomain.PULSe) \n
		Defines how the waveform period is defined, as a time duration or as a number of pulses. \n
			:param base: PULSe| TIME
		"""
		param = Conversions.enum_scalar_to_str(base, enums.BaseDomain)
		self._core.io.write(f'IPM:WAVeform:BASE {param}')

	def get_count(self) -> float:
		"""SCPI: IPM:WAVeform:COUNt \n
		Snippet: value: float = driver.ipm.waveform.get_count() \n
		Sets the waveform period as number of pulses. \n
			:return: count: integer Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('IPM:WAVeform:COUNt?')
		return Conversions.str_to_float(response)

	def set_count(self, count: float) -> None:
		"""SCPI: IPM:WAVeform:COUNt \n
		Snippet: driver.ipm.waveform.set_count(count = 1.0) \n
		Sets the waveform period as number of pulses. \n
			:param count: integer Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(count)
		self._core.io.write(f'IPM:WAVeform:COUNt {param}')

	def get_offset(self) -> float:
		"""SCPI: IPM:WAVeform:OFFSet \n
		Snippet: value: float = driver.ipm.waveform.get_offset() \n
		Shifts the profile by the selected offset. \n
			:return: offset: float Range: -1e+09 to 1e+09
		"""
		response = self._core.io.query_str('IPM:WAVeform:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, offset: float) -> None:
		"""SCPI: IPM:WAVeform:OFFSet \n
		Snippet: driver.ipm.waveform.set_offset(offset = 1.0) \n
		Shifts the profile by the selected offset. \n
			:param offset: float Range: -1e+09 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(offset)
		self._core.io.write(f'IPM:WAVeform:OFFSet {param}')

	def get_period(self) -> float:
		"""SCPI: IPM:WAVeform:PERiod \n
		Snippet: value: float = driver.ipm.waveform.get_period() \n
		Sets the waveform period. \n
			:return: period: float Range: 1e-09 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('IPM:WAVeform:PERiod?')
		return Conversions.str_to_float(response)

	def set_period(self, period: float) -> None:
		"""SCPI: IPM:WAVeform:PERiod \n
		Snippet: driver.ipm.waveform.set_period(period = 1.0) \n
		Sets the waveform period. \n
			:param period: float Range: 1e-09 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(period)
		self._core.io.write(f'IPM:WAVeform:PERiod {param}')

	def get_phase(self) -> float:
		"""SCPI: IPM:WAVeform:PHASe \n
		Snippet: value: float = driver.ipm.waveform.get_phase() \n
		Enables a phase offset to change the start phase of the sine wave. \n
			:return: phase: float Range: -1e+09 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('IPM:WAVeform:PHASe?')
		return Conversions.str_to_float(response)

	def set_phase(self, phase: float) -> None:
		"""SCPI: IPM:WAVeform:PHASe \n
		Snippet: driver.ipm.waveform.set_phase(phase = 1.0) \n
		Enables a phase offset to change the start phase of the sine wave. \n
			:param phase: float Range: -1e+09 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(phase)
		self._core.io.write(f'IPM:WAVeform:PHASe {param}')

	def get_pkpk(self) -> float:
		"""SCPI: IPM:WAVeform:PKPK \n
		Snippet: value: float = driver.ipm.waveform.get_pkpk() \n
		Sets the value range of the linear ramp profile or the period of the sine profile. \n
			:return: pkpk: float Range: 1e-09 to 1e+09, Unit: sec
		"""
		response = self._core.io.query_str('IPM:WAVeform:PKPK?')
		return Conversions.str_to_float(response)

	def set_pkpk(self, pkpk: float) -> None:
		"""SCPI: IPM:WAVeform:PKPK \n
		Snippet: driver.ipm.waveform.set_pkpk(pkpk = 1.0) \n
		Sets the value range of the linear ramp profile or the period of the sine profile. \n
			:param pkpk: float Range: 1e-09 to 1e+09, Unit: sec
		"""
		param = Conversions.decimal_value_to_str(pkpk)
		self._core.io.write(f'IPM:WAVeform:PKPK {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.WaveformShape:
		"""SCPI: IPM:WAVeform:TYPE \n
		Snippet: value: enums.WaveformShape = driver.ipm.waveform.get_type_py() \n
		Sets the profile shape. \n
			:return: type_py: RAMP| SINE| TRIangular
		"""
		response = self._core.io.query_str('IPM:WAVeform:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.WaveformShape)

	def set_type_py(self, type_py: enums.WaveformShape) -> None:
		"""SCPI: IPM:WAVeform:TYPE \n
		Snippet: driver.ipm.waveform.set_type_py(type_py = enums.WaveformShape.RAMP) \n
		Sets the profile shape. \n
			:param type_py: RAMP| SINE| TRIangular
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.WaveformShape)
		self._core.io.write(f'IPM:WAVeform:TYPE {param}')
