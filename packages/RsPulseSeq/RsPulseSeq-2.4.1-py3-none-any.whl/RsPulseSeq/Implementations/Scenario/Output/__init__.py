from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Output:
	"""Output commands group definition. 25 total commands, 7 Subgroups, 11 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("output", core, parent)

	@property
	def arb(self):
		"""arb commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_arb'):
			from .Arb import Arb
			self._arb = Arb(self._core, self._cmd_group)
		return self._arb

	@property
	def clock(self):
		"""clock commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_clock'):
			from .Clock import Clock
			self._clock = Clock(self._core, self._cmd_group)
		return self._clock

	@property
	def duration(self):
		"""duration commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_duration'):
			from .Duration import Duration
			self._duration = Duration(self._core, self._cmd_group)
		return self._duration

	@property
	def marker(self):
		"""marker commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_marker'):
			from .Marker import Marker
			self._marker = Marker(self._core, self._cmd_group)
		return self._marker

	@property
	def recall(self):
		"""recall commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_recall'):
			from .Recall import Recall
			self._recall = Recall(self._core, self._cmd_group)
		return self._recall

	@property
	def reset(self):
		"""reset commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_reset'):
			from .Reset import Reset
			self._reset = Reset(self._core, self._cmd_group)
		return self._reset

	@property
	def supress(self):
		"""supress commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_supress'):
			from .Supress import Supress
			self._supress = Supress(self._core, self._cmd_group)
		return self._supress

	def get_clipping(self) -> float:
		"""SCPI: SCENario:OUTPut:CLIPping \n
		Snippet: value: float = driver.scenario.output.get_clipping() \n
		Sets a maximum level to limit the dynamic range of the signal. Pulses at levels above this threshold are reduced
		(clipped) to the configured level. \n
			:return: clipping: float Range: -100 to 20, Unit: dBm
		"""
		response = self._core.io.query_str('SCENario:OUTPut:CLIPping?')
		return Conversions.str_to_float(response)

	def set_clipping(self, clipping: float) -> None:
		"""SCPI: SCENario:OUTPut:CLIPping \n
		Snippet: driver.scenario.output.set_clipping(clipping = 1.0) \n
		Sets a maximum level to limit the dynamic range of the signal. Pulses at levels above this threshold are reduced
		(clipped) to the configured level. \n
			:param clipping: float Range: -100 to 20, Unit: dBm
		"""
		param = Conversions.decimal_value_to_str(clipping)
		self._core.io.write(f'SCENario:OUTPut:CLIPping {param}')

	# noinspection PyTypeChecker
	def get_format_py(self) -> enums.OutFormat:
		"""SCPI: SCENario:OUTPut:FORMat \n
		Snippet: value: enums.OutFormat = driver.scenario.output.get_format_py() \n
		Sets the type of the generated waveform file. \n
			:return: format_py: WV| MSW
		"""
		response = self._core.io.query_str('SCENario:OUTPut:FORMat?')
		return Conversions.str_to_scalar_enum(response, enums.OutFormat)

	def set_format_py(self, format_py: enums.OutFormat) -> None:
		"""SCPI: SCENario:OUTPut:FORMat \n
		Snippet: driver.scenario.output.set_format_py(format_py = enums.OutFormat.ESEQencing) \n
		Sets the type of the generated waveform file. \n
			:param format_py: WV| MSW
		"""
		param = Conversions.enum_scalar_to_str(format_py, enums.OutFormat)
		self._core.io.write(f'SCENario:OUTPut:FORMat {param}')

	def get_frequency(self) -> float:
		"""SCPI: SCENario:OUTPut:FREQuency \n
		Snippet: value: float = driver.scenario.output.get_frequency() \n
		Sets the carrier RF frequency of the generated signal. \n
			:return: frequency: float Range: 1000 to 4.4e+10
		"""
		response = self._core.io.query_str('SCENario:OUTPut:FREQuency?')
		return Conversions.str_to_float(response)

	def set_frequency(self, frequency: float) -> None:
		"""SCPI: SCENario:OUTPut:FREQuency \n
		Snippet: driver.scenario.output.set_frequency(frequency = 1.0) \n
		Sets the carrier RF frequency of the generated signal. \n
			:param frequency: float Range: 1000 to 4.4e+10
		"""
		param = Conversions.decimal_value_to_str(frequency)
		self._core.io.write(f'SCENario:OUTPut:FREQuency {param}')

	def get_level(self) -> float:
		"""SCPI: SCENario:OUTPut:LEVel \n
		Snippet: value: float = driver.scenario.output.get_level() \n
		Sets the reference level used by the calculation of the pulse envelope. \n
			:return: level: float Range: -130 to 30
		"""
		response = self._core.io.query_str('SCENario:OUTPut:LEVel?')
		return Conversions.str_to_float(response)

	def set_level(self, level: float) -> None:
		"""SCPI: SCENario:OUTPut:LEVel \n
		Snippet: driver.scenario.output.set_level(level = 1.0) \n
		Sets the reference level used by the calculation of the pulse envelope. \n
			:param level: float Range: -130 to 30
		"""
		param = Conversions.decimal_value_to_str(level)
		self._core.io.write(f'SCENario:OUTPut:LEVel {param}')

	# noinspection PyTypeChecker
	def get_mt_mode(self) -> enums.AutoManualMode:
		"""SCPI: SCENario:OUTPut:MTMode \n
		Snippet: value: enums.AutoManualMode = driver.scenario.output.get_mt_mode() \n
		If multithreading is enabled with method RsPulseSeq.Scenario.Output.multithread, sets the mode to use for multithreading. \n
			:return: mt_mode: AUTO| MANual
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MTMode?')
		return Conversions.str_to_scalar_enum(response, enums.AutoManualMode)

	def set_mt_mode(self, mt_mode: enums.AutoManualMode) -> None:
		"""SCPI: SCENario:OUTPut:MTMode \n
		Snippet: driver.scenario.output.set_mt_mode(mt_mode = enums.AutoManualMode.AUTO) \n
		If multithreading is enabled with method RsPulseSeq.Scenario.Output.multithread, sets the mode to use for multithreading. \n
			:param mt_mode: AUTO| MANual
		"""
		param = Conversions.enum_scalar_to_str(mt_mode, enums.AutoManualMode)
		self._core.io.write(f'SCENario:OUTPut:MTMode {param}')

	def get_mt_threads(self) -> float:
		"""SCPI: SCENario:OUTPut:MTTHreads \n
		Snippet: value: float = driver.scenario.output.get_mt_threads() \n
		In manual mode, sets the required number of threads for the signal calculation. \n
			:return: mt_threads: float Range: 0 to 1000
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MTTHreads?')
		return Conversions.str_to_float(response)

	def set_mt_threads(self, mt_threads: float) -> None:
		"""SCPI: SCENario:OUTPut:MTTHreads \n
		Snippet: driver.scenario.output.set_mt_threads(mt_threads = 1.0) \n
		In manual mode, sets the required number of threads for the signal calculation. \n
			:param mt_threads: float Range: 0 to 1000
		"""
		param = Conversions.decimal_value_to_str(mt_threads)
		self._core.io.write(f'SCENario:OUTPut:MTTHreads {param}')

	def get_multithread(self) -> bool:
		"""SCPI: SCENario:OUTPut:MULTithread \n
		Snippet: value: bool = driver.scenario.output.get_multithread() \n
		Enable to optmize the calculation speed. \n
			:return: multithread: ON| OFF| 1| 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:MULTithread?')
		return Conversions.str_to_bool(response)

	def set_multithread(self, multithread: bool) -> None:
		"""SCPI: SCENario:OUTPut:MULTithread \n
		Snippet: driver.scenario.output.set_multithread(multithread = False) \n
		Enable to optmize the calculation speed. \n
			:param multithread: ON| OFF| 1| 0
		"""
		param = Conversions.bool_to_str(multithread)
		self._core.io.write(f'SCENario:OUTPut:MULTithread {param}')

	def get_path(self) -> str:
		"""SCPI: SCENario:OUTPut:PATH \n
		Snippet: value: str = driver.scenario.output.get_path() \n
		Sets the directory the generated waveform is stored in. \n
			:return: path: string File path
		"""
		response = self._core.io.query_str('SCENario:OUTPut:PATH?')
		return trim_str_response(response)

	def set_path(self, path: str) -> None:
		"""SCPI: SCENario:OUTPut:PATH \n
		Snippet: driver.scenario.output.set_path(path = '1') \n
		Sets the directory the generated waveform is stored in. \n
			:param path: string File path
		"""
		param = Conversions.value_to_quoted_str(path)
		self._core.io.write(f'SCENario:OUTPut:PATH {param}')

	# noinspection PyTypeChecker
	def get_run_mode(self) -> enums.RepeatMode:
		"""SCPI: SCENario:OUTPut:RUNMode \n
		Snippet: value: enums.RepeatMode = driver.scenario.output.get_run_mode() \n
		Defines the way the generated signal is processed. \n
			:return: run_mode: CONTinuous| SINGle
		"""
		response = self._core.io.query_str('SCENario:OUTPut:RUNMode?')
		return Conversions.str_to_scalar_enum(response, enums.RepeatMode)

	def set_run_mode(self, run_mode: enums.RepeatMode) -> None:
		"""SCPI: SCENario:OUTPut:RUNMode \n
		Snippet: driver.scenario.output.set_run_mode(run_mode = enums.RepeatMode.CONTinuous) \n
		Defines the way the generated signal is processed. \n
			:param run_mode: CONTinuous| SINGle
		"""
		param = Conversions.enum_scalar_to_str(run_mode, enums.RepeatMode)
		self._core.io.write(f'SCENario:OUTPut:RUNMode {param}')

	# noinspection PyTypeChecker
	def get_target(self) -> enums.TargetOut:
		"""SCPI: SCENario:OUTPut:TARGet \n
		Snippet: value: enums.TargetOut = driver.scenario.output.get_target() \n
		Defines whether the software creates an ARB file or transfers the generated waveform to a connected physical generator.
		To assign a generator, use the command method RsPulseSeq.Scenario.Generator.value. To set the name and the directory the
		ARB file is stored in, use the command method RsPulseSeq.Scenario.Output.path. \n
			:return: target: INSTrument| FILE
		"""
		response = self._core.io.query_str('SCENario:OUTPut:TARGet?')
		return Conversions.str_to_scalar_enum(response, enums.TargetOut)

	def set_target(self, target: enums.TargetOut) -> None:
		"""SCPI: SCENario:OUTPut:TARGet \n
		Snippet: driver.scenario.output.set_target(target = enums.TargetOut.FILE) \n
		Defines whether the software creates an ARB file or transfers the generated waveform to a connected physical generator.
		To assign a generator, use the command method RsPulseSeq.Scenario.Generator.value. To set the name and the directory the
		ARB file is stored in, use the command method RsPulseSeq.Scenario.Output.path. \n
			:param target: INSTrument| FILE
		"""
		param = Conversions.enum_scalar_to_str(target, enums.TargetOut)
		self._core.io.write(f'SCENario:OUTPut:TARGet {param}')

	def get_threshold(self) -> float:
		"""SCPI: SCENario:OUTPut:THReshold \n
		Snippet: value: float = driver.scenario.output.get_threshold() \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:return: threshold: float Range: -100 to 0
		"""
		response = self._core.io.query_str('SCENario:OUTPut:THReshold?')
		return Conversions.str_to_float(response)

	def set_threshold(self, threshold: float) -> None:
		"""SCPI: SCENario:OUTPut:THReshold \n
		Snippet: driver.scenario.output.set_threshold(threshold = 1.0) \n
		Sets a threshold. Pulses at levels below this threshold are omitted. \n
			:param threshold: float Range: -100 to 0
		"""
		param = Conversions.decimal_value_to_str(threshold)
		self._core.io.write(f'SCENario:OUTPut:THReshold {param}')

	def clone(self) -> 'Output':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = Output(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
