from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Condition:
	"""Condition commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("condition", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.Condition:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:TYPE \n
		Snippet: value: enums.Condition = driver.sequence.item.marker.condition.get_type_py() \n
		Sets the sign in the logical condition. \n
			:return: type_py: SMALler| GREater| EQUal| NOTequal
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:CONDition:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.Condition)

	def set_type_py(self, type_py: enums.Condition) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:TYPE \n
		Snippet: driver.sequence.item.marker.condition.set_type_py(type_py = enums.Condition.EQUal) \n
		Sets the sign in the logical condition. \n
			:param type_py: SMALler| GREater| EQUal| NOTequal
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.Condition)
		self._core.io.write(f'SEQuence:ITEM:MARKer:CONDition:TYPE {param}')

	def get_string_value(self) -> str:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:VALue \n
		Snippet: value: str = driver.sequence.item.marker.condition.get_string_value() \n
		Sets the numerical value used with the comparison. \n
			:return: value: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:CONDition:VALue?')
		return trim_str_response(response)

	def set_string_value(self, value: str) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:VALue \n
		Snippet: driver.sequence.item.marker.condition.set_string_value(value = '1') \n
		Sets the numerical value used with the comparison. \n
			:param value: string
		"""
		param = Conversions.value_to_quoted_str(value)
		self._core.io.write(f'SEQuence:ITEM:MARKer:CONDition:VALue {param}')

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:VARiable \n
		Snippet: value: str = driver.sequence.item.marker.condition.get_variable() \n
		Defines the value that is compared with the fixed values set with the command method RsPulseSeq.Sequence.Item.Marker.
		Condition.stringValue. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:CONDition:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition:VARiable \n
		Snippet: driver.sequence.item.marker.condition.set_variable(variable = '1') \n
		Defines the value that is compared with the fixed values set with the command method RsPulseSeq.Sequence.Item.Marker.
		Condition.stringValue. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:MARKer:CONDition:VARiable {param}')

	def get_value(self) -> float:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition \n
		Snippet: value: float = driver.sequence.item.marker.condition.get_value() \n
		Enables up to four markers of the corresponding type. \n
			:return: condition: No help available
		"""
		response = self._core.io.query_str('SEQuence:ITEM:MARKer:CONDition?')
		return Conversions.str_to_float(response)

	def set_value(self, condition: float) -> None:
		"""SCPI: SEQuence:ITEM:MARKer:CONDition \n
		Snippet: driver.sequence.item.marker.condition.set_value(condition = 1.0) \n
		Enables up to four markers of the corresponding type. \n
			:param condition: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(condition)
		self._core.io.write(f'SEQuence:ITEM:MARKer:CONDition {param}')
