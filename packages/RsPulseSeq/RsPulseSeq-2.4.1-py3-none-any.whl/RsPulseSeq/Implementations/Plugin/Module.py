from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Module:
	"""Module commands group definition. 6 total commands, 0 Subgroups, 6 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("module", core, parent)

	def get_author(self) -> str:
		"""SCPI: PLUGin:MODule:AUTHor \n
		Snippet: value: str = driver.plugin.module.get_author() \n
		Queries information on the loaded file. The query returns information as specified in the description of the
		corresponding function in 'Plug-in programming API'. The following are the possible values for the type query. \n
			:return: author: REPort| IPM | MOP MOP Plugin for IPM Plugin for REPort Plugin for reports created during the waveform generation
		"""
		response = self._core.io.query_str('PLUGin:MODule:AUTHor?')
		return trim_str_response(response)

	def get_comment(self) -> str:
		"""SCPI: PLUGin:MODule:COMMent \n
		Snippet: value: str = driver.plugin.module.get_comment() \n
		Queries information on the loaded file. The query returns information as specified in the description of the
		corresponding function in 'Plug-in programming API'. The following are the possible values for the type query. \n
			:return: comment: REPort| IPM | MOP MOP Plugin for IPM Plugin for REPort Plugin for reports created during the waveform generation
		"""
		response = self._core.io.query_str('PLUGin:MODule:COMMent?')
		return trim_str_response(response)

	def get_data(self) -> float:
		"""SCPI: PLUGin:MODule:DATA \n
		Snippet: value: float = driver.plugin.module.get_data() \n
		Queries whether the plugin requires data from a data source. \n
			:return: data: 0 | 1 0 Data source is not required 1 Data source is required
		"""
		response = self._core.io.query_str('PLUGin:MODule:DATA?')
		return Conversions.str_to_float(response)

	def get_name(self) -> str:
		"""SCPI: PLUGin:MODule:NAME \n
		Snippet: value: str = driver.plugin.module.get_name() \n
		Renames the selected repository element. \n
			:return: name: string Must be unique for the particular type of repository elements. May contain empty spaces.
		"""
		response = self._core.io.query_str('PLUGin:MODule:NAME?')
		return trim_str_response(response)

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.ModuleType:
		"""SCPI: PLUGin:MODule:TYPE \n
		Snippet: value: enums.ModuleType = driver.plugin.module.get_type_py() \n
		Queries information on the loaded file. The query returns information as specified in the description of the
		corresponding function in 'Plug-in programming API'. The following are the possible values for the type query. \n
			:return: type_py: REPort| IPM | MOP MOP Plugin for IPM Plugin for REPort Plugin for reports created during the waveform generation
		"""
		response = self._core.io.query_str('PLUGin:MODule:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ModuleType)

	def get_version(self) -> str:
		"""SCPI: PLUGin:MODule:VERSion \n
		Snippet: value: str = driver.plugin.module.get_version() \n
		Queries information on the loaded file. The query returns information as specified in the description of the
		corresponding function in 'Plug-in programming API'. The following are the possible values for the type query. \n
			:return: version: REPort| IPM | MOP MOP Plugin for IPM Plugin for REPort Plugin for reports created during the waveform generation
		"""
		response = self._core.io.query_str('PLUGin:MODule:VERSion?')
		return trim_str_response(response)
