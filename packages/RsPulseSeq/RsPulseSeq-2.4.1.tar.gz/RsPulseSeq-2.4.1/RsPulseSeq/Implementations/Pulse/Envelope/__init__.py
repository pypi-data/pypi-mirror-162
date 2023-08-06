from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Envelope:
	"""Envelope commands group definition. 13 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("envelope", core, parent)

	@property
	def data(self):
		"""data commands group. 1 Sub-classes, 6 commands."""
		if not hasattr(self, '_data'):
			from .Data import Data
			self._data = Data(self._core, self._cmd_group)
		return self._data

	def get_equation(self) -> str:
		"""SCPI: PULSe:ENVelope:EQUation \n
		Snippet: value: str = driver.pulse.envelope.get_equation() \n
		Determines the envelope mathematically. \n
			:return: equation: string
		"""
		response = self._core.io.query_str('PULSe:ENVelope:EQUation?')
		return trim_str_response(response)

	def set_equation(self, equation: str) -> None:
		"""SCPI: PULSe:ENVelope:EQUation \n
		Snippet: driver.pulse.envelope.set_equation(equation = '1') \n
		Determines the envelope mathematically. \n
			:param equation: string
		"""
		param = Conversions.value_to_quoted_str(equation)
		self._core.io.write(f'PULSe:ENVelope:EQUation {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.EnvelopeMode:
		"""SCPI: PULSe:ENVelope:MODE \n
		Snippet: value: enums.EnvelopeMode = driver.pulse.envelope.get_mode() \n
		Selects the type of the custom envelope function. \n
			:return: mode: DATA| EQUation
		"""
		response = self._core.io.query_str('PULSe:ENVelope:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.EnvelopeMode)

	def set_mode(self, mode: enums.EnvelopeMode) -> None:
		"""SCPI: PULSe:ENVelope:MODE \n
		Snippet: driver.pulse.envelope.set_mode(mode = enums.EnvelopeMode.DATA) \n
		Selects the type of the custom envelope function. \n
			:param mode: DATA| EQUation
		"""
		param = Conversions.enum_scalar_to_str(mode, enums.EnvelopeMode)
		self._core.io.write(f'PULSe:ENVelope:MODE {param}')

	def clone(self) -> 'Envelope':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Envelope(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
