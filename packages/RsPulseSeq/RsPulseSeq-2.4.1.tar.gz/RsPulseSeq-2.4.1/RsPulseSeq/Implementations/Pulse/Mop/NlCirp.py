from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NlCirp:
	"""NlCirp commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("nlCirp", core, parent)

	def get_equation(self) -> str:
		"""SCPI: PULSe:MOP:NLCHirp:EQUation \n
		Snippet: value: str = driver.pulse.mop.nlCirp.get_equation() \n
		Determines the chirp mathematically. \n
			:return: equation: string
		"""
		response = self._core.io.query_str('PULSe:MOP:NLCHirp:EQUation?')
		return trim_str_response(response)

	def set_equation(self, equation: str) -> None:
		"""SCPI: PULSe:MOP:NLCHirp:EQUation \n
		Snippet: driver.pulse.mop.nlCirp.set_equation(equation = '1') \n
		Determines the chirp mathematically. \n
			:param equation: string
		"""
		param = Conversions.value_to_quoted_str(equation)
		self._core.io.write(f'PULSe:MOP:NLCHirp:EQUation {param}')
