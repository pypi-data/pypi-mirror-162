from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Utilities import trim_str_response
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Target:
	"""Target commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("target", core, parent)

	# noinspection PyTypeChecker
	def get_parameter(self) -> enums.TargetParam:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:PARameter \n
		Snippet: value: enums.TargetParam = driver.sequence.item.ipm.target.get_parameter() \n
		Sets the pulse parameter to that the IPM variation is assigned. \n
			:return: parameter: LEVel| RLEVel| SRATe| FREQuency| PRI| WIDTh| FALL| AMFRequency| FMDeviation| DELay| FSKDeviation| PRF| FMFRequency| CDEViation| PHASe| RISE| AMDepth | DROop| RFRequency| OVERshoot
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:TARGet:PARameter?')
		return Conversions.str_to_scalar_enum(response, enums.TargetParam)

	def set_parameter(self, parameter: enums.TargetParam) -> None:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:PARameter \n
		Snippet: driver.sequence.item.ipm.target.set_parameter(parameter = enums.TargetParam.AMDepth) \n
		Sets the pulse parameter to that the IPM variation is assigned. \n
			:param parameter: LEVel| RLEVel| SRATe| FREQuency| PRI| WIDTh| FALL| AMFRequency| FMDeviation| DELay| FSKDeviation| PRF| FMFRequency| CDEViation| PHASe| RISE| AMDepth | DROop| RFRequency| OVERshoot
		"""
		param = Conversions.enum_scalar_to_str(parameter, enums.TargetParam)
		self._core.io.write(f'SEQuence:ITEM:IPM:TARGet:PARameter {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.TargetType:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:TYPE \n
		Snippet: value: enums.TargetType = driver.sequence.item.ipm.target.get_type_py() \n
		Sets whether the profile is assigned to a parameter or to a variable. \n
			:return: type_py: PARameter| VARiable
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:TARGet:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.TargetType)

	def set_type_py(self, type_py: enums.TargetType) -> None:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:TYPE \n
		Snippet: driver.sequence.item.ipm.target.set_type_py(type_py = enums.TargetType.PARameter) \n
		Sets whether the profile is assigned to a parameter or to a variable. \n
			:param type_py: PARameter| VARiable
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.TargetType)
		self._core.io.write(f'SEQuence:ITEM:IPM:TARGet:TYPE {param}')

	def get_variable(self) -> str:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:VARiable \n
		Snippet: value: str = driver.sequence.item.ipm.target.get_variable() \n
		Sets the variable to that the variation is assigned. \n
			:return: variable: string
		"""
		response = self._core.io.query_str('SEQuence:ITEM:IPM:TARGet:VARiable?')
		return trim_str_response(response)

	def set_variable(self, variable: str) -> None:
		"""SCPI: SEQuence:ITEM:IPM:TARGet:VARiable \n
		Snippet: driver.sequence.item.ipm.target.set_variable(variable = '1') \n
		Sets the variable to that the variation is assigned. \n
			:param variable: string
		"""
		param = Conversions.value_to_quoted_str(variable)
		self._core.io.write(f'SEQuence:ITEM:IPM:TARGet:VARiable {param}')
