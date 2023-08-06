from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Path:
	"""Path commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("path", core, parent)

	def get_calculated(self) -> str:
		"""SCPI: PROGram:PATH:CALCulated \n
		Snippet: value: str = driver.program.path.get_calculated() \n
		Sets the directory that holds the calculated waveforms. \n
			:return: calculated: string
		"""
		response = self._core.io.query_str('PROGram:PATH:CALCulated?')
		return trim_str_response(response)

	def set_calculated(self, calculated: str) -> None:
		"""SCPI: PROGram:PATH:CALCulated \n
		Snippet: driver.program.path.set_calculated(calculated = '1') \n
		Sets the directory that holds the calculated waveforms. \n
			:param calculated: string
		"""
		param = Conversions.value_to_quoted_str(calculated)
		self._core.io.write(f'PROGram:PATH:CALCulated {param}')

	def get_install(self) -> str:
		"""SCPI: PROGram:PATH:INSTall \n
		Snippet: value: str = driver.program.path.get_install() \n
		Queries the storage location for repository files. \n
			:return: install: string
		"""
		response = self._core.io.query_str('PROGram:PATH:INSTall?')
		return trim_str_response(response)

	def get_report(self) -> str:
		"""SCPI: PROGram:PATH:REPort \n
		Snippet: value: str = driver.program.path.get_report() \n
		Sets the directory that holds generated reports. \n
			:return: report: string
		"""
		response = self._core.io.query_str('PROGram:PATH:REPort?')
		return trim_str_response(response)

	def set_report(self, report: str) -> None:
		"""SCPI: PROGram:PATH:REPort \n
		Snippet: driver.program.path.set_report(report = '1') \n
		Sets the directory that holds generated reports. \n
			:param report: string
		"""
		param = Conversions.value_to_quoted_str(report)
		self._core.io.write(f'PROGram:PATH:REPort {param}')

	def get_volatile(self) -> str:
		"""SCPI: PROGram:PATH:VOLatile \n
		Snippet: value: str = driver.program.path.get_volatile() \n
		Sets the directory that holds volatile data. \n
			:return: volatile: string
		"""
		response = self._core.io.query_str('PROGram:PATH:VOLatile?')
		return trim_str_response(response)

	def set_volatile(self, volatile: str) -> None:
		"""SCPI: PROGram:PATH:VOLatile \n
		Snippet: driver.program.path.set_volatile(volatile = '1') \n
		Sets the directory that holds volatile data. \n
			:param volatile: string
		"""
		param = Conversions.value_to_quoted_str(volatile)
		self._core.io.write(f'PROGram:PATH:VOLatile {param}')
