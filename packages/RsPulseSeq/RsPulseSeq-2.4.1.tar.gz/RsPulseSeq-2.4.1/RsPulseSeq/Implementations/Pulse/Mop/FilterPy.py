from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FilterPy:
	"""FilterPy commands group definition. 5 total commands, 0 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("filterPy", core, parent)

	def get_bt(self) -> float:
		"""SCPI: PULSe:MOP:FILTer:BT \n
		Snippet: value: float = driver.pulse.mop.filterPy.get_bt() \n
		Sets the B x T filter parameter. \n
			:return: bt: float Range: 0.15 to 2.5
		"""
		response = self._core.io.query_str('PULSe:MOP:FILTer:BT?')
		return Conversions.str_to_float(response)

	def set_bt(self, bt: float) -> None:
		"""SCPI: PULSe:MOP:FILTer:BT \n
		Snippet: driver.pulse.mop.filterPy.set_bt(bt = 1.0) \n
		Sets the B x T filter parameter. \n
			:param bt: float Range: 0.15 to 2.5
		"""
		param = Conversions.decimal_value_to_str(bt)
		self._core.io.write(f'PULSe:MOP:FILTer:BT {param}')

	def get_bandwidth(self) -> float:
		"""SCPI: PULSe:MOP:FILTer:BWIDth \n
		Snippet: value: float = driver.pulse.mop.filterPy.get_bandwidth() \n
		Sets the transition bandwidth of the filter. \n
			:return: bwidth: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:FILTer:BWIDth?')
		return Conversions.str_to_float(response)

	def set_bandwidth(self, bwidth: float) -> None:
		"""SCPI: PULSe:MOP:FILTer:BWIDth \n
		Snippet: driver.pulse.mop.filterPy.set_bandwidth(bwidth = 1.0) \n
		Sets the transition bandwidth of the filter. \n
			:param bwidth: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(bwidth)
		self._core.io.write(f'PULSe:MOP:FILTer:BWIDth {param}')

	def get_length(self) -> float:
		"""SCPI: PULSe:MOP:FILTer:LENGth \n
		Snippet: value: float = driver.pulse.mop.filterPy.get_length() \n
		Sets the filter length. \n
			:return: length: integer Range: 1 to 64
		"""
		response = self._core.io.query_str('PULSe:MOP:FILTer:LENGth?')
		return Conversions.str_to_float(response)

	def set_length(self, length: float) -> None:
		"""SCPI: PULSe:MOP:FILTer:LENGth \n
		Snippet: driver.pulse.mop.filterPy.set_length(length = 1.0) \n
		Sets the filter length. \n
			:param length: integer Range: 1 to 64
		"""
		param = Conversions.decimal_value_to_str(length)
		self._core.io.write(f'PULSe:MOP:FILTer:LENGth {param}')

	def get_rolloff(self) -> float:
		"""SCPI: PULSe:MOP:FILTer:ROLLoff \n
		Snippet: value: float = driver.pulse.mop.filterPy.get_rolloff() \n
		Sets the roll off factor. \n
			:return: rolloff: float Range: 0.05 to 1
		"""
		response = self._core.io.query_str('PULSe:MOP:FILTer:ROLLoff?')
		return Conversions.str_to_float(response)

	def set_rolloff(self, rolloff: float) -> None:
		"""SCPI: PULSe:MOP:FILTer:ROLLoff \n
		Snippet: driver.pulse.mop.filterPy.set_rolloff(rolloff = 1.0) \n
		Sets the roll off factor. \n
			:param rolloff: float Range: 0.05 to 1
		"""
		param = Conversions.decimal_value_to_str(rolloff)
		self._core.io.write(f'PULSe:MOP:FILTer:ROLLoff {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.FilterType:
		"""SCPI: PULSe:MOP:FILTer:TYPE \n
		Snippet: value: enums.FilterType = driver.pulse.mop.filterPy.get_type_py() \n
		Selects the filter type. \n
			:return: type_py: NONE| RECTangular| COS| RCOS| GAUSs| LPASs| FSKGauss| SOQPsk| SMWRect
		"""
		response = self._core.io.query_str('PULSe:MOP:FILTer:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.FilterType)

	def set_type_py(self, type_py: enums.FilterType) -> None:
		"""SCPI: PULSe:MOP:FILTer:TYPE \n
		Snippet: driver.pulse.mop.filterPy.set_type_py(type_py = enums.FilterType.COS) \n
		Selects the filter type. \n
			:param type_py: NONE| RECTangular| COS| RCOS| GAUSs| LPASs| FSKGauss| SOQPsk| SMWRect
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.FilterType)
		self._core.io.write(f'PULSe:MOP:FILTer:TYPE {param}')
