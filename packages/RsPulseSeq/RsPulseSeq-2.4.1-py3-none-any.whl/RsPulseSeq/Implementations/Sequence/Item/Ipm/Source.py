from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Source:
	"""Source commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.SourceType:
		"""SCPI: SEQuence:ITEM:IPM:SOURce:TYPE \n
		Snippet: value: enums.SourceType = driver.sequence.item.ipm.source.get_type_py() \n
		Sets whether the variation is defined as a profile or as a variable. \n
			:return: type_py: PROFile| VARiable
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:SOURce:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.SourceType)

	def set_type_py(self, type_py: enums.SourceType) -> None:
		"""SCPI: SEQuence:ITEM:IPM:SOURce:TYPE \n
		Snippet: driver.sequence.item.ipm.source.set_type_py(type_py = enums.SourceType.PROFile) \n
		Sets whether the variation is defined as a profile or as a variable. \n
			:param type_py: PROFile| VARiable
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.SourceType)
		self._core.io.write(f'SEQuence:ITEM:IPM:SOURce:TYPE {param}')

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:IPM:SOURce:VARiable \n
		Snippet: value: str = driver.sequence.item.ipm.source.get_variable() \n
		Sets the variable that defines the variation. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:SOURce:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:IPM:SOURce:VARiable \n
		Snippet: driver.sequence.item.ipm.source.set_variable(variable = '1') \n
		Sets the variable that defines the variation. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:IPM:SOURce:VARiable {param}')

	def get_value(self) -> str:
		"""SCPI: SEQuence:ITEM:IPM:SOURce \n
		Snippet: value: str = driver.sequence.item.ipm.source.get_value() \n
		Selects the profile source. Use the command method RsPulseSeq.Ipm.catalog to querry the existing profiles. \n
			:return: source: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:SOURce?')
		return trim_str_response(response)

	def set_value(self, source: str) -> None:
		"""SCPI: SEQuence:ITEM:IPM:SOURce \n
		Snippet: driver.sequence.item.ipm.source.set_value(source = '1') \n
		Selects the profile source. Use the command method RsPulseSeq.Ipm.catalog to querry the existing profiles. \n
			:param source: string
		"""
		param = Conversions.value_to_quoted_str(source)
		self._core.io.write(f'SEQuence:ITEM:IPM:SOURce {param}')
