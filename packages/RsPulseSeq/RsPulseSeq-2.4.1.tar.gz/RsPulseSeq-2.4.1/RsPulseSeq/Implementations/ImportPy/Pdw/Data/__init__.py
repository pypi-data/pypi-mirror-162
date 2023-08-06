from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Data:
	"""Data commands group definition. 34 total commands, 9 Subgroups, 8 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	@property
	def am(self):
		"""am commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_am'):
			from .Am import Am
			self._am = Am(self._core, self._cmd_group)
		return self._am

	@property
	def ask(self):
		"""ask commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_ask'):
			from .Ask import Ask
			self._ask = Ask(self._core, self._cmd_group)
		return self._ask

	@property
	def cph(self):
		"""cph commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_cph'):
			from .Cph import Cph
			self._cph = Cph(self._core, self._cmd_group)
		return self._cph

	@property
	def fm(self):
		"""fm commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_fm'):
			from .Fm import Fm
			self._fm = Fm(self._core, self._cmd_group)
		return self._fm

	@property
	def fsk(self):
		"""fsk commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_fsk'):
			from .Fsk import Fsk
			self._fsk = Fsk(self._core, self._cmd_group)
		return self._fsk

	@property
	def lfm(self):
		"""lfm commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_lfm'):
			from .Lfm import Lfm
			self._lfm = Lfm(self._core, self._cmd_group)
		return self._lfm

	@property
	def nlFm(self):
		"""nlFm commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_nlFm'):
			from .NlFm import NlFm
			self._nlFm = NlFm(self._core, self._cmd_group)
		return self._nlFm

	@property
	def plFm(self):
		"""plFm commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_plFm'):
			from .PlFm import PlFm
			self._plFm = PlFm(self._core, self._cmd_group)
		return self._plFm

	@property
	def psk(self):
		"""psk commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_psk'):
			from .Psk import Psk
			self._psk = Psk(self._core, self._cmd_group)
		return self._psk

	def get_frequency(self) -> float:
		"""SCPI: IMPort:PDW:DATA:FREQuency \n
		Snippet: value: float = driver.importPy.pdw.data.get_frequency() \n
		Queries the pulse parameter. \n
			:return: frequency: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:FREQuency?')
		return Conversions.str_to_float(response)

	def get_level(self) -> float:
		"""SCPI: IMPort:PDW:DATA:LEVel \n
		Snippet: value: float = driver.importPy.pdw.data.get_level() \n
		Queries the pulse parameter. \n
			:return: level: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:LEVel?')
		return Conversions.str_to_float(response)

	# noinspection PyTypeChecker
	def get_mop(self) -> enums.DataMop:
		"""SCPI: IMPort:PDW:DATA:MOP \n
		Snippet: value: enums.DataMop = driver.importPy.pdw.data.get_mop() \n
		Queries the used modulation on pulse (MOP) . Use the corresponding command to query further pulse and modulation
		parameter for the respective MOP. \n
			:return: mop: CW| AM| FM| ASK| FSK| PSK| LFM| NLFM| TFM| BKR2a| BKR2b| BKR3| BKR4a| BKR4b| BKR5| BKR7| BKR11| BKR13| CPH| PLFM
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:MOP?')
		return Conversions.str_to_scalar_enum(response, enums.DataMop)

	def get_offset(self) -> float:
		"""SCPI: IMPort:PDW:DATA:OFFSet \n
		Snippet: value: float = driver.importPy.pdw.data.get_offset() \n
		Queries the pulse parameter. \n
			:return: offset: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:OFFSet?')
		return Conversions.str_to_float(response)

	def get_phase(self) -> float:
		"""SCPI: IMPort:PDW:DATA:PHASe \n
		Snippet: value: float = driver.importPy.pdw.data.get_phase() \n
		Queries the pulse parameter. \n
			:return: phase: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:PHASe?')
		return Conversions.str_to_float(response)

	def get_sel(self) -> float:
		"""SCPI: IMPort:PDW:DATA:SEL \n
		Snippet: value: float = driver.importPy.pdw.data.get_sel() \n
		Selects the pulse for that the further queries apply. \n
			:return: sel: float Range: 1 to max
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:SEL?')
		return Conversions.str_to_float(response)

	def set_sel(self, sel: float) -> None:
		"""SCPI: IMPort:PDW:DATA:SEL \n
		Snippet: driver.importPy.pdw.data.set_sel(sel = 1.0) \n
		Selects the pulse for that the further queries apply. \n
			:param sel: float Range: 1 to max
		"""
		param = Conversions.decimal_value_to_str(sel)
		self._core.io.write(f'IMPort:PDW:DATA:SEL {param}')

	def get_toa(self) -> float:
		"""SCPI: IMPort:PDW:DATA:TOA \n
		Snippet: value: float = driver.importPy.pdw.data.get_toa() \n
		Queries the pulse parameter. \n
			:return: toa: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:TOA?')
		return Conversions.str_to_float(response)

	def get_width(self) -> float:
		"""SCPI: IMPort:PDW:DATA:WIDTh \n
		Snippet: value: float = driver.importPy.pdw.data.get_width() \n
		Queries the pulse parameter. \n
			:return: width: float
		"""
		response = self._core.io.query_str('IMPort:PDW:DATA:WIDTh?')
		return Conversions.str_to_float(response)

	def clone(self) -> 'Data':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Data(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
