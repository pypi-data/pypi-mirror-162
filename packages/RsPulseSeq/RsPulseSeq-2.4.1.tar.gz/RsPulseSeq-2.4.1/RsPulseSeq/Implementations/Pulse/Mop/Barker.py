from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Barker:
	"""Barker commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("barker", core, parent)

	def get_blank(self) -> bool:
		"""SCPI: PULSe:MOP:BARKer:BLANk \n
		Snippet: value: bool = driver.pulse.mop.barker.get_blank() \n
		Blanks out the signal during the transition time. \n
			:return: blank: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('PULSe:MOP:BARKer:BLANk?')
		return Conversions.str_to_bool(response)

	def set_blank(self, blank: bool) -> None:
		"""SCPI: PULSe:MOP:BARKer:BLANk \n
		Snippet: driver.pulse.mop.barker.set_blank(blank = False) \n
		Blanks out the signal during the transition time. \n
			:param blank: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(blank)
		self._core.io.write(f'PULSe:MOP:BARKer:BLANk {param}')

	# noinspection PyTypeChecker
	def get_code(self) -> enums.BarkerCode:
		"""SCPI: PULSe:MOP:BARKer:CODE \n
		Snippet: value: enums.BarkerCode = driver.pulse.mop.barker.get_code() \n
		Selects the code sequence. \n
			:return: code: R2A| R2B| R3| R4A| R4B| R5| R7| R11| R13
		"""
		response = self._core.io.query_str('PULSe:MOP:BARKer:CODE?')
		return Conversions.str_to_scalar_enum(response, enums.BarkerCode)

	def set_code(self, code: enums.BarkerCode) -> None:
		"""SCPI: PULSe:MOP:BARKer:CODE \n
		Snippet: driver.pulse.mop.barker.set_code(code = enums.BarkerCode.R11) \n
		Selects the code sequence. \n
			:param code: R2A| R2B| R3| R4A| R4B| R5| R7| R11| R13
		"""
		param = Conversions.enum_scalar_to_str(code, enums.BarkerCode)
		self._core.io.write(f'PULSe:MOP:BARKer:CODE {param}')

	def get_ttime(self) -> float:
		"""SCPI: PULSe:MOP:BARKer:TTIMe \n
		Snippet: value: float = driver.pulse.mop.barker.get_ttime() \n
		Sets the transition time. \n
			:return: ttime: float Range: 0 to 50, Unit: percent
		"""
		response = self._core.io.query_str('PULSe:MOP:BARKer:TTIMe?')
		return Conversions.str_to_float(response)

	def set_ttime(self, ttime: float) -> None:
		"""SCPI: PULSe:MOP:BARKer:TTIMe \n
		Snippet: driver.pulse.mop.barker.set_ttime(ttime = 1.0) \n
		Sets the transition time. \n
			:param ttime: float Range: 0 to 50, Unit: percent
		"""
		param = Conversions.decimal_value_to_str(ttime)
		self._core.io.write(f'PULSe:MOP:BARKer:TTIMe {param}')
