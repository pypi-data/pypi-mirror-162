from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePy:
	"""TypePy commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	# noinspection PyTypeChecker
	def get_fall(self) -> enums.PulseType:
		"""SCPI: PULSe:TYPE:FALL \n
		Snippet: value: enums.PulseType = driver.pulse.typePy.get_fall() \n
		Sets the slope type for the rising and falling edges. \n
			:return: fall: No help available
		"""
		response = self._core.io.query_str('PULSe:TYPE:FALL?')
		return Conversions.str_to_scalar_enum(response, enums.PulseType)

	def set_fall(self, fall: enums.PulseType) -> None:
		"""SCPI: PULSe:TYPE:FALL \n
		Snippet: driver.pulse.typePy.set_fall(fall = enums.PulseType.COSine) \n
		Sets the slope type for the rising and falling edges. \n
			:param fall: LINear| COSine| RCOSine| SQRT
		"""
		param = Conversions.enum_scalar_to_str(fall, enums.PulseType)
		self._core.io.write(f'PULSe:TYPE:FALL {param}')

	# noinspection PyTypeChecker
	def get_rise(self) -> enums.PulseType:
		"""SCPI: PULSe:TYPE:RISE \n
		Snippet: value: enums.PulseType = driver.pulse.typePy.get_rise() \n
		Sets the slope type for the rising and falling edges. \n
			:return: rise: LINear| COSine| RCOSine| SQRT
		"""
		response = self._core.io.query_str('PULSe:TYPE:RISE?')
		return Conversions.str_to_scalar_enum(response, enums.PulseType)

	def set_rise(self, rise: enums.PulseType) -> None:
		"""SCPI: PULSe:TYPE:RISE \n
		Snippet: driver.pulse.typePy.set_rise(rise = enums.PulseType.COSine) \n
		Sets the slope type for the rising and falling edges. \n
			:param rise: LINear| COSine| RCOSine| SQRT
		"""
		param = Conversions.enum_scalar_to_str(rise, enums.PulseType)
		self._core.io.write(f'PULSe:TYPE:RISE {param}')
