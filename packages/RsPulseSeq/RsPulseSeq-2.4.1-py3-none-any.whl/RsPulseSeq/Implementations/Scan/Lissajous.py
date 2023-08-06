from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Lissajous:
	"""Lissajous commands group definition. 7 total commands, 0 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("lissajous", core, parent)

	def get_am_px(self) -> float:
		"""SCPI: SCAN:LISSajous:AMPX \n
		Snippet: value: float = driver.scan.lissajous.get_am_px() \n
		Sets the magnitudes of two harmonic vibrations. \n
			:return: am_px: No help available
		"""
		response = self._core.io.query_str('SCAN:LISSajous:AMPX?')
		return Conversions.str_to_float(response)

	def set_am_px(self, am_px: float) -> None:
		"""SCPI: SCAN:LISSajous:AMPX \n
		Snippet: driver.scan.lissajous.set_am_px(am_px = 1.0) \n
		Sets the magnitudes of two harmonic vibrations. \n
			:param am_px: float Range: 0.01 to 45
		"""
		param = Conversions.decimal_value_to_str(am_px)
		self._core.io.write(f'SCAN:LISSajous:AMPX {param}')

	def get_am_pz(self) -> float:
		"""SCPI: SCAN:LISSajous:AMPZ \n
		Snippet: value: float = driver.scan.lissajous.get_am_pz() \n
		Sets the magnitudes of two harmonic vibrations. \n
			:return: am_pz: float Range: 0.01 to 45
		"""
		response = self._core.io.query_str('SCAN:LISSajous:AMPZ?')
		return Conversions.str_to_float(response)

	def set_am_pz(self, am_pz: float) -> None:
		"""SCPI: SCAN:LISSajous:AMPZ \n
		Snippet: driver.scan.lissajous.set_am_pz(am_pz = 1.0) \n
		Sets the magnitudes of two harmonic vibrations. \n
			:param am_pz: float Range: 0.01 to 45
		"""
		param = Conversions.decimal_value_to_str(am_pz)
		self._core.io.write(f'SCAN:LISSajous:AMPZ {param}')

	def get_freq(self) -> float:
		"""SCPI: SCAN:LISSajous:FREQ \n
		Snippet: value: float = driver.scan.lissajous.get_freq() \n
		Sets the base frequency. \n
			:return: freq: float Range: 0.01 to 1000
		"""
		response = self._core.io.query_str('SCAN:LISSajous:FREQ?')
		return Conversions.str_to_float(response)

	def set_freq(self, freq: float) -> None:
		"""SCPI: SCAN:LISSajous:FREQ \n
		Snippet: driver.scan.lissajous.set_freq(freq = 1.0) \n
		Sets the base frequency. \n
			:param freq: float Range: 0.01 to 1000
		"""
		param = Conversions.decimal_value_to_str(freq)
		self._core.io.write(f'SCAN:LISSajous:FREQ {param}')

	def get_phix(self) -> float:
		"""SCPI: SCAN:LISSajous:PHIX \n
		Snippet: value: float = driver.scan.lissajous.get_phix() \n
		Sets the phases of the two harmonic vibrations. \n
			:return: phix: No help available
		"""
		response = self._core.io.query_str('SCAN:LISSajous:PHIX?')
		return Conversions.str_to_float(response)

	def set_phix(self, phix: float) -> None:
		"""SCPI: SCAN:LISSajous:PHIX \n
		Snippet: driver.scan.lissajous.set_phix(phix = 1.0) \n
		Sets the phases of the two harmonic vibrations. \n
			:param phix: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(phix)
		self._core.io.write(f'SCAN:LISSajous:PHIX {param}')

	def get_phiz(self) -> float:
		"""SCPI: SCAN:LISSajous:PHIZ \n
		Snippet: value: float = driver.scan.lissajous.get_phiz() \n
		Sets the phases of the two harmonic vibrations. \n
			:return: phiz: float Range: 0 to 360
		"""
		response = self._core.io.query_str('SCAN:LISSajous:PHIZ?')
		return Conversions.str_to_float(response)

	def set_phiz(self, phiz: float) -> None:
		"""SCPI: SCAN:LISSajous:PHIZ \n
		Snippet: driver.scan.lissajous.set_phiz(phiz = 1.0) \n
		Sets the phases of the two harmonic vibrations. \n
			:param phiz: float Range: 0 to 360
		"""
		param = Conversions.decimal_value_to_str(phiz)
		self._core.io.write(f'SCAN:LISSajous:PHIZ {param}')

	def get_xfactor(self) -> float:
		"""SCPI: SCAN:LISSajous:XFACtor \n
		Snippet: value: float = driver.scan.lissajous.get_xfactor() \n
		Sets the ratio between the two angular frequencies. \n
			:return: xfactor: No help available
		"""
		response = self._core.io.query_str('SCAN:LISSajous:XFACtor?')
		return Conversions.str_to_float(response)

	def set_xfactor(self, xfactor: float) -> None:
		"""SCPI: SCAN:LISSajous:XFACtor \n
		Snippet: driver.scan.lissajous.set_xfactor(xfactor = 1.0) \n
		Sets the ratio between the two angular frequencies. \n
			:param xfactor: float Range: 1 to 10
		"""
		param = Conversions.decimal_value_to_str(xfactor)
		self._core.io.write(f'SCAN:LISSajous:XFACtor {param}')

	def get_zfactor(self) -> float:
		"""SCPI: SCAN:LISSajous:ZFACtor \n
		Snippet: value: float = driver.scan.lissajous.get_zfactor() \n
		Sets the ratio between the two angular frequencies. \n
			:return: zfactor: float Range: 1 to 10
		"""
		response = self._core.io.query_str('SCAN:LISSajous:ZFACtor?')
		return Conversions.str_to_float(response)

	def set_zfactor(self, zfactor: float) -> None:
		"""SCPI: SCAN:LISSajous:ZFACtor \n
		Snippet: driver.scan.lissajous.set_zfactor(zfactor = 1.0) \n
		Sets the ratio between the two angular frequencies. \n
			:param zfactor: float Range: 1 to 10
		"""
		param = Conversions.decimal_value_to_str(zfactor)
		self._core.io.write(f'SCAN:LISSajous:ZFACtor {param}')
