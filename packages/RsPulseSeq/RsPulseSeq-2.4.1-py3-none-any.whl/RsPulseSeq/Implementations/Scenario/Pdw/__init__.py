from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Pdw:
	"""Pdw commands group definition. 16 total commands, 2 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pdw", core, parent)

	@property
	def amMos(self):
		"""amMos commands group. 1 Sub-classes, 3 commands."""
		if not hasattr(self, '_amMos'):
			from .AmMos import AmMos
			self._amMos = AmMos(self._core, self._cmd_group)
		return self._amMos

	@property
	def plugin(self):
		"""plugin commands group. 1 Sub-classes, 1 commands."""
		if not hasattr(self, '_plugin'):
			from .Plugin import Plugin
			self._plugin = Plugin(self._core, self._cmd_group)
		return self._plugin

	def get_enable(self) -> bool:
		"""SCPI: SCENario:PDW:ENABle \n
		Snippet: value: bool = driver.scenario.pdw.get_enable() \n
		Enables generation of Pulse Descripter Word (PDW) reports. \n
			:return: enable: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:PDW:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, enable: bool) -> None:
		"""SCPI: SCENario:PDW:ENABle \n
		Snippet: driver.scenario.pdw.set_enable(enable = False) \n
		Enables generation of Pulse Descripter Word (PDW) reports. \n
			:param enable: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(enable)
		self._core.io.write(f'SCENario:PDW:ENABle {param}')

	def get_host(self) -> str:
		"""SCPI: SCENario:PDW:HOST \n
		Snippet: value: str = driver.scenario.pdw.get_host() \n
		Select a connected signal generator, with all options required for the scenario, to allow reporting. \n
			:return: host: string
		"""
		response = self._core.io.query_str('SCENario:PDW:HOST?')
		return trim_str_response(response)

	def set_host(self, host: str) -> None:
		"""SCPI: SCENario:PDW:HOST \n
		Snippet: driver.scenario.pdw.set_host(host = '1') \n
		Select a connected signal generator, with all options required for the scenario, to allow reporting. \n
			:param host: string
		"""
		param = Conversions.value_to_quoted_str(host)
		self._core.io.write(f'SCENario:PDW:HOST {param}')

	def get_path(self) -> str:
		"""SCPI: SCENario:PDW:PATH \n
		Snippet: value: str = driver.scenario.pdw.get_path() \n
		Sets the target directory in that the generated report files are stored. \n
			:return: path: string
		"""
		response = self._core.io.query_str('SCENario:PDW:PATH?')
		return trim_str_response(response)

	def set_path(self, path: str) -> None:
		"""SCPI: SCENario:PDW:PATH \n
		Snippet: driver.scenario.pdw.set_path(path = '1') \n
		Sets the target directory in that the generated report files are stored. \n
			:param path: string
		"""
		param = Conversions.value_to_quoted_str(path)
		self._core.io.write(f'SCENario:PDW:PATH {param}')

	def get_template(self) -> str:
		"""SCPI: SCENario:PDW:TEMPlate \n
		Snippet: value: str = driver.scenario.pdw.get_template() \n
		Edits the selected template. \n
			:return: template: string
		"""
		response = self._core.io.query_str('SCENario:PDW:TEMPlate?')
		return trim_str_response(response)

	def set_template(self, template: str) -> None:
		"""SCPI: SCENario:PDW:TEMPlate \n
		Snippet: driver.scenario.pdw.set_template(template = '1') \n
		Edits the selected template. \n
			:param template: string
		"""
		param = Conversions.value_to_quoted_str(template)
		self._core.io.write(f'SCENario:PDW:TEMPlate {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.PwdType:
		"""SCPI: SCENario:PDW:TYPE \n
		Snippet: value: enums.PwdType = driver.scenario.pdw.get_type_py() \n
		Sets the template used be the reporting function. \n
			:return: type_py: DEFault| TEMPlate| PLUGin| AMMos
		"""
		response = self._core.io.query_str('SCENario:PDW:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.PwdType)

	def set_type_py(self, type_py: enums.PwdType) -> None:
		"""SCPI: SCENario:PDW:TYPE \n
		Snippet: driver.scenario.pdw.set_type_py(type_py = enums.PwdType.AMMos) \n
		Sets the template used be the reporting function. \n
			:param type_py: DEFault| TEMPlate| PLUGin| AMMos
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.PwdType)
		self._core.io.write(f'SCENario:PDW:TYPE {param}')

	def clone(self) -> 'Pdw':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Pdw(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
