from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Marker:
	"""Marker commands group definition. 7 total commands, 0 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("marker", core, parent)

	def get_auto(self) -> float:
		"""SCPI: PULSe:MARKer:AUTO \n
		Snippet: value: float = driver.pulse.marker.get_auto() \n
		Enables up to four restart markers. \n
			:return: auto: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		response = self._core.io.query_str('PULSe:MARKer:AUTO?')
		return Conversions.str_to_float(response)

	def set_auto(self, auto: float) -> None:
		"""SCPI: PULSe:MARKer:AUTO \n
		Snippet: driver.pulse.marker.set_auto(auto = 1.0) \n
		Enables up to four restart markers. \n
			:param auto: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(auto)
		self._core.io.write(f'PULSe:MARKer:AUTO {param}')

	def get_fall(self) -> float:
		"""SCPI: PULSe:MARKer:FALL \n
		Snippet: value: float = driver.pulse.marker.get_fall() \n
		Enables up to four restart markers. \n
			:return: fall: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:FALL?')
		return Conversions.str_to_float(response)

	def set_fall(self, fall: float) -> None:
		"""SCPI: PULSe:MARKer:FALL \n
		Snippet: driver.pulse.marker.set_fall(fall = 1.0) \n
		Enables up to four restart markers. \n
			:param fall: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(fall)
		self._core.io.write(f'PULSe:MARKer:FALL {param}')

	def get_gate(self) -> float:
		"""SCPI: PULSe:MARKer:GATE \n
		Snippet: value: float = driver.pulse.marker.get_gate() \n
		Enables up to four restart markers. \n
			:return: gate: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:GATE?')
		return Conversions.str_to_float(response)

	def set_gate(self, gate: float) -> None:
		"""SCPI: PULSe:MARKer:GATE \n
		Snippet: driver.pulse.marker.set_gate(gate = 1.0) \n
		Enables up to four restart markers. \n
			:param gate: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(gate)
		self._core.io.write(f'PULSe:MARKer:GATE {param}')

	def get_post(self) -> float:
		"""SCPI: PULSe:MARKer:POST \n
		Snippet: value: float = driver.pulse.marker.get_post() \n
		Enables up to four restart markers. \n
			:return: post: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:POST?')
		return Conversions.str_to_float(response)

	def set_post(self, post: float) -> None:
		"""SCPI: PULSe:MARKer:POST \n
		Snippet: driver.pulse.marker.set_post(post = 1.0) \n
		Enables up to four restart markers. \n
			:param post: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(post)
		self._core.io.write(f'PULSe:MARKer:POST {param}')

	def get_pre(self) -> float:
		"""SCPI: PULSe:MARKer:PRE \n
		Snippet: value: float = driver.pulse.marker.get_pre() \n
		Enables up to four restart markers. \n
			:return: pre: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:PRE?')
		return Conversions.str_to_float(response)

	def set_pre(self, pre: float) -> None:
		"""SCPI: PULSe:MARKer:PRE \n
		Snippet: driver.pulse.marker.set_pre(pre = 1.0) \n
		Enables up to four restart markers. \n
			:param pre: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(pre)
		self._core.io.write(f'PULSe:MARKer:PRE {param}')

	def get_rise(self) -> float:
		"""SCPI: PULSe:MARKer:RISE \n
		Snippet: value: float = driver.pulse.marker.get_rise() \n
		Enables up to four restart markers. \n
			:return: rise: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:RISE?')
		return Conversions.str_to_float(response)

	def set_rise(self, rise: float) -> None:
		"""SCPI: PULSe:MARKer:RISE \n
		Snippet: driver.pulse.marker.set_rise(rise = 1.0) \n
		Enables up to four restart markers. \n
			:param rise: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(rise)
		self._core.io.write(f'PULSe:MARKer:RISE {param}')

	def get_width(self) -> float:
		"""SCPI: PULSe:MARKer:WIDTh \n
		Snippet: value: float = driver.pulse.marker.get_width() \n
		Enables up to four restart markers. \n
			:return: width: No help available
		"""
		response = self._core.io.query_str('PULSe:MARKer:WIDTh?')
		return Conversions.str_to_float(response)

	def set_width(self, width: float) -> None:
		"""SCPI: PULSe:MARKer:WIDTh \n
		Snippet: driver.pulse.marker.set_width(width = 1.0) \n
		Enables up to four restart markers. \n
			:param width: float See Table 'Setting parameter as function of the marker states'. Range: 0 to 65535
		"""
		param = Conversions.decimal_value_to_str(width)
		self._core.io.write(f'PULSe:MARKer:WIDTh {param}')
