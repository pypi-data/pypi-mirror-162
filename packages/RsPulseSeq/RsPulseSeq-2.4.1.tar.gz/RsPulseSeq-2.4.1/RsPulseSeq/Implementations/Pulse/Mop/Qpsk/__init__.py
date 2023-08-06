from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Qpsk:
	"""Qpsk commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("qpsk", core, parent)

	@property
	def soQpsk(self):
		"""soQpsk commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_soQpsk'):
			from .SoQpsk import SoQpsk
			self._soQpsk = SoQpsk(self._core, self._cmd_group)
		return self._soQpsk

	def get_symbol_rate(self) -> float:
		"""SCPI: PULSe:MOP:QPSK:SRATe \n
		Snippet: value: float = driver.pulse.mop.qpsk.get_symbol_rate() \n
		Sets the symbol rate. \n
			:return: srate: float Range: 1 to 1e+09
		"""
		response = self._core.io.query_str('PULSe:MOP:QPSK:SRATe?')
		return Conversions.str_to_float(response)

	def set_symbol_rate(self, srate: float) -> None:
		"""SCPI: PULSe:MOP:QPSK:SRATe \n
		Snippet: driver.pulse.mop.qpsk.set_symbol_rate(srate = 1.0) \n
		Sets the symbol rate. \n
			:param srate: float Range: 1 to 1e+09
		"""
		param = Conversions.decimal_value_to_str(srate)
		self._core.io.write(f'PULSe:MOP:QPSK:SRATe {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.QpskType:
		"""SCPI: PULSe:MOP:QPSK:TYPE \n
		Snippet: value: enums.QpskType = driver.pulse.mop.qpsk.get_type_py() \n
		Selects the modulation type. \n
			:return: type_py: NORMal| OQPSk| DQPSk| ASOQpsk| BSOQpsk| TGSoqpsk
		"""
		response = self._core.io.query_str('PULSe:MOP:QPSK:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.QpskType)

	def set_type_py(self, type_py: enums.QpskType) -> None:
		"""SCPI: PULSe:MOP:QPSK:TYPE \n
		Snippet: driver.pulse.mop.qpsk.set_type_py(type_py = enums.QpskType.ASOQpsk) \n
		Selects the modulation type. \n
			:param type_py: NORMal| OQPSk| DQPSk| ASOQpsk| BSOQpsk| TGSoqpsk
		"""
		param = Conversions.enum_scalar_to_str(type_py, enums.QpskType)
		self._core.io.write(f'PULSe:MOP:QPSK:TYPE {param}')

	def clone(self) -> 'Qpsk':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Qpsk(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
