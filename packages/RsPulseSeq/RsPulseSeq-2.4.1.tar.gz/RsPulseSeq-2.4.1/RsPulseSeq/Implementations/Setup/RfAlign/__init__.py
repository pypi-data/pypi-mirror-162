from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RfAlign:
	"""RfAlign commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rfAlign", core, parent)

	@property
	def importPy(self):
		"""importPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_importPy'):
			from .ImportPy import ImportPy
			self._importPy = ImportPy(self._core, self._cmd_group)
		return self._importPy

	def get_instrument(self) -> str:
		"""SCPI: SETup:RFALign:INSTrument \n
		Snippet: value: str = driver.setup.rfAlign.get_instrument() \n
		Selects the instrument or computer from that the RF port alignment setup file is loaded. \n
			:return: instrument: string IP address or the hostname
		"""
		response = self._core.io.query_str('SETup:RFALign:INSTrument?')
		return trim_str_response(response)

	def set_instrument(self, instrument: str) -> None:
		"""SCPI: SETup:RFALign:INSTrument \n
		Snippet: driver.setup.rfAlign.set_instrument(instrument = '1') \n
		Selects the instrument or computer from that the RF port alignment setup file is loaded. \n
			:param instrument: string IP address or the hostname
		"""
		param = Conversions.value_to_quoted_str(instrument)
		self._core.io.write(f'SETup:RFALign:INSTrument {param}')

	def get_setup(self) -> str:
		"""SCPI: SETup:RFALign:SETup \n
		Snippet: value: str = driver.setup.rfAlign.get_setup() \n
		Selects the setup file to be laded. Setup files are files with predefined file format, content and the extension *.rfsa.
		For details, see the user manual of the corresponding base unit. \n
			:return: setup: string Complete file path with file name, incl. file extension
		"""
		response = self._core.io.query_str('SETup:RFALign:SETup?')
		return trim_str_response(response)

	def set_setup(self, setup: str) -> None:
		"""SCPI: SETup:RFALign:SETup \n
		Snippet: driver.setup.rfAlign.set_setup(setup = '1') \n
		Selects the setup file to be laded. Setup files are files with predefined file format, content and the extension *.rfsa.
		For details, see the user manual of the corresponding base unit. \n
			:param setup: string Complete file path with file name, incl. file extension
		"""
		param = Conversions.value_to_quoted_str(setup)
		self._core.io.write(f'SETup:RFALign:SETup {param}')

	def clone(self) -> 'RfAlign':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RfAlign(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
