from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Time:
	"""Time commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def get_fall(self) -> float:
		"""SCPI: PULSe:TIME:FALL \n
		Snippet: value: float = driver.pulse.time.get_fall() \n
		Sets the transition time of the rising and falling edges. \n
			:return: fall: No help available
		"""
		response = self._core.io.query_str('PULSe:TIME:FALL?')
		return Conversions.str_to_float(response)

	def set_fall(self, fall: float) -> None:
		"""SCPI: PULSe:TIME:FALL \n
		Snippet: driver.pulse.time.set_fall(fall = 1.0) \n
		Sets the transition time of the rising and falling edges. \n
			:param fall: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(fall)
		self._core.io.write(f'PULSe:TIME:FALL {param}')

	def get_post(self) -> float:
		"""SCPI: PULSe:TIME:POST \n
		Snippet: value: float = driver.pulse.time.get_post() \n
		Sets the marker's duration. \n
			:return: post: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('PULSe:TIME:POST?')
		return Conversions.str_to_float(response)

	def set_post(self, post: float) -> None:
		"""SCPI: PULSe:TIME:POST \n
		Snippet: driver.pulse.time.set_post(post = 1.0) \n
		Sets the marker's duration. \n
			:param post: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(post)
		self._core.io.write(f'PULSe:TIME:POST {param}')

	def get_pre(self) -> float:
		"""SCPI: PULSe:TIME:PRE \n
		Snippet: value: float = driver.pulse.time.get_pre() \n
		Sets the marker's duration. Value different than zero shifts the start of the pulse rising edge and the entire pulse. \n
			:return: pre: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('PULSe:TIME:PRE?')
		return Conversions.str_to_float(response)

	def set_pre(self, pre: float) -> None:
		"""SCPI: PULSe:TIME:PRE \n
		Snippet: driver.pulse.time.set_pre(pre = 1.0) \n
		Sets the marker's duration. Value different than zero shifts the start of the pulse rising edge and the entire pulse. \n
			:param pre: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(pre)
		self._core.io.write(f'PULSe:TIME:PRE {param}')

	# noinspection PyTypeChecker
	def get_reference(self) -> enums.TimeReference:
		"""SCPI: PULSe:TIME:REFerence \n
		Snippet: value: enums.TimeReference = driver.pulse.time.get_reference() \n
		Selects a predefined envelope profile. \n
			:return: reference: VOLTage| POWer| FULL
		"""
		response = self._core.io.query_str('PULSe:TIME:REFerence?')
		return Conversions.str_to_scalar_enum(response, enums.TimeReference)

	def set_reference(self, reference: enums.TimeReference) -> None:
		"""SCPI: PULSe:TIME:REFerence \n
		Snippet: driver.pulse.time.set_reference(reference = enums.TimeReference.FULL) \n
		Selects a predefined envelope profile. \n
			:param reference: VOLTage| POWer| FULL
		"""
		param = Conversions.enum_scalar_to_str(reference, enums.TimeReference)
		self._core.io.write(f'PULSe:TIME:REFerence {param}')

	def get_rise(self) -> float:
		"""SCPI: PULSe:TIME:RISE \n
		Snippet: value: float = driver.pulse.time.get_rise() \n
		Sets the transition time of the rising and falling edges. \n
			:return: rise: float Range: 0 to 3600
		"""
		response = self._core.io.query_str('PULSe:TIME:RISE?')
		return Conversions.str_to_float(response)

	def set_rise(self, rise: float) -> None:
		"""SCPI: PULSe:TIME:RISE \n
		Snippet: driver.pulse.time.set_rise(rise = 1.0) \n
		Sets the transition time of the rising and falling edges. \n
			:param rise: float Range: 0 to 3600
		"""
		param = Conversions.decimal_value_to_str(rise)
		self._core.io.write(f'PULSe:TIME:RISE {param}')

	def get_width(self) -> float:
		"""SCPI: PULSe:TIME:WIDTh \n
		Snippet: value: float = driver.pulse.time.get_width() \n
		Sets the time during that the pulse is on top power. \n
			:return: width: float Range: 0 to 3600, Unit: s
		"""
		response = self._core.io.query_str('PULSe:TIME:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: PULSe:TIME:WIDTh \n
		Snippet: driver.pulse.time.set_width(width = 1.0) \n
		Sets the time during that the pulse is on top power. \n
			:param width: float Range: 0 to 3600, Unit: s
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'PULSe:TIME:WIDTh {param}')
