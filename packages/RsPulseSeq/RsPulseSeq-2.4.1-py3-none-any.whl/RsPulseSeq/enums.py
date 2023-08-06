from enum import Enum


# noinspection SpellCheckingInspection
class AmType(Enum):
	"""4 Members, LSB ... USB"""
	LSB = 0
	SB = 1
	STD = 2
	USB = 3


# noinspection SpellCheckingInspection
class AntennaModel(Enum):
	"""12 Members, ARRay ... USER"""
	ARRay = 0
	CARDoid = 1
	CARRay = 2
	COSecant = 3
	CUSTom = 4
	DIPole = 5
	GAUSsian = 6
	HORN = 7
	PARabolic = 8
	PLUGin = 9
	SINC = 10
	USER = 11


# noinspection SpellCheckingInspection
class AntennaModelArray(Enum):
	"""8 Members, COSine ... UNIForm"""
	COSine = 0
	COSN = 1
	CSQuared = 2
	HAMMing = 3
	HANN = 4
	PARabolic = 5
	TRIangular = 6
	UNIForm = 7


# noinspection SpellCheckingInspection
class Attitude(Enum):
	"""3 Members, CONStant ... WAYPoint"""
	CONStant = 0
	MOTion = 1
	WAYPoint = 2


# noinspection SpellCheckingInspection
class AutoManualMode(Enum):
	"""2 Members, AUTO ... MANual"""
	AUTO = 0
	MANual = 1


# noinspection SpellCheckingInspection
class Azimuth(Enum):
	"""2 Members, BEARing ... RX"""
	BEARing = 0
	RX = 1


# noinspection SpellCheckingInspection
class BarkerCode(Enum):
	"""9 Members, R11 ... R7"""
	R11 = 0
	R13 = 1
	R2A = 2
	R2B = 3
	R3 = 4
	R4A = 5
	R4B = 6
	R5 = 7
	R7 = 8


# noinspection SpellCheckingInspection
class BaseDomain(Enum):
	"""2 Members, PULSe ... TIME"""
	PULSe = 0
	TIME = 1


# noinspection SpellCheckingInspection
class BaseDomainB(Enum):
	"""2 Members, LENGth ... TIME"""
	LENGth = 0
	TIME = 1


# noinspection SpellCheckingInspection
class BbSync(Enum):
	"""3 Members, CTRigger ... UNSYnc"""
	CTRigger = 0
	TRIGger = 1
	UNSYnc = 2


# noinspection SpellCheckingInspection
class BlockSize(Enum):
	"""6 Members, _16K ... _64K"""
	_16K = 0
	_1M = 1
	_2M = 2
	_32K = 3
	_4M = 4
	_64K = 5


# noinspection SpellCheckingInspection
class BlType(Enum):
	"""2 Members, MIRRor ... OMNidirect"""
	MIRRor = 0
	OMNidirect = 1


# noinspection SpellCheckingInspection
class BpskTtype(Enum):
	"""2 Members, COSine ... LINear"""
	COSine = 0
	LINear = 1


# noinspection SpellCheckingInspection
class BpskType(Enum):
	"""2 Members, CONStant ... STANdard"""
	CONStant = 0
	STANdard = 1


# noinspection SpellCheckingInspection
class BufferSize(Enum):
	"""6 Members, _128M ... _64M"""
	_128M = 0
	_16M = 1
	_1G = 2
	_256M = 3
	_512M = 4
	_64M = 5


# noinspection SpellCheckingInspection
class ChirpType(Enum):
	"""5 Members, DOWN ... UP"""
	DOWN = 0
	PIECewise = 1
	SINE = 2
	TRIangular = 3
	UP = 4


# noinspection SpellCheckingInspection
class CircularMode(Enum):
	"""2 Members, RPM ... SEC"""
	RPM = 0
	SEC = 1


# noinspection SpellCheckingInspection
class Coding(Enum):
	"""4 Members, DGRay ... NONE"""
	DGRay = 0
	DIFFerential = 1
	GRAY = 2
	NONE = 3


# noinspection SpellCheckingInspection
class Complexity(Enum):
	"""3 Members, DIRection ... PTRain"""
	DIRection = 0
	EMITter = 1
	PTRain = 2


# noinspection SpellCheckingInspection
class Condition(Enum):
	"""4 Members, EQUal ... SMALler"""
	EQUal = 0
	GREater = 1
	NOTequal = 2
	SMALler = 3


# noinspection SpellCheckingInspection
class DataMop(Enum):
	"""20 Members, AM ... TFM"""
	AM = 0
	ASK = 1
	BKR11 = 2
	BKR13 = 3
	BKR2a = 4
	BKR2b = 5
	BKR3 = 6
	BKR4a = 7
	BKR4b = 8
	BKR5 = 9
	BKR7 = 10
	CPH = 11
	CW = 12
	FM = 13
	FSK = 14
	LFM = 15
	NLFM = 16
	PLFM = 17
	PSK = 18
	TFM = 19


# noinspection SpellCheckingInspection
class DataUnit(Enum):
	"""3 Members, DB ... WATTs"""
	DB = 0
	VOLTage = 1
	WATTs = 2


# noinspection SpellCheckingInspection
class DfType(Enum):
	"""4 Members, BACKground ... WAVeform"""
	BACKground = 0
	EMITter = 1
	PLATform = 2
	WAVeform = 3


# noinspection SpellCheckingInspection
class EnvelopeMode(Enum):
	"""2 Members, DATA ... EQUation"""
	DATA = 0
	EQUation = 1


# noinspection SpellCheckingInspection
class ExcMode(Enum):
	"""3 Members, LEVel ... WIDTh"""
	LEVel = 0
	TIME = 1
	WIDTh = 2


# noinspection SpellCheckingInspection
class FillerMode(Enum):
	"""2 Members, DURation ... TSYNc"""
	DURation = 0
	TSYNc = 1


# noinspection SpellCheckingInspection
class FillerSignal(Enum):
	"""3 Members, BLANk ... HOLD"""
	BLANk = 0
	CW = 1
	HOLD = 2


# noinspection SpellCheckingInspection
class FillerTime(Enum):
	"""2 Members, EQUation ... FIXed"""
	EQUation = 0
	FIXed = 1


# noinspection SpellCheckingInspection
class FilterType(Enum):
	"""9 Members, COS ... SOQPsk"""
	COS = 0
	FSKGauss = 1
	GAUSs = 2
	LPASs = 3
	NONE = 4
	RCOS = 5
	RECTangular = 6
	SMWRect = 7
	SOQPsk = 8


# noinspection SpellCheckingInspection
class FskType(Enum):
	"""6 Members, FS16 ... FS8"""
	FS16 = 0
	FS2 = 1
	FS32 = 2
	FS4 = 3
	FS64 = 4
	FS8 = 5


# noinspection SpellCheckingInspection
class GeneratorType(Enum):
	"""8 Members, SGT ... SW"""
	SGT = 0
	SMBB = 1
	SMBV = 2
	SMJ = 3
	SMM = 4
	SMU = 5
	SMW = 6
	SW = 7


# noinspection SpellCheckingInspection
class Geometry(Enum):
	"""4 Members, CIRCular ... RECTangular"""
	CIRCular = 0
	HEXagonal = 1
	LINear = 2
	RECTangular = 3


# noinspection SpellCheckingInspection
class HqMode(Enum):
	"""2 Members, NORMal ... TABLe"""
	NORMal = 0
	TABLe = 1


# noinspection SpellCheckingInspection
class InterleaveMode(Enum):
	"""2 Members, DROP ... MERGe"""
	DROP = 0
	MERGe = 1


# noinspection SpellCheckingInspection
class Interpolation(Enum):
	"""2 Members, LINear ... NONE"""
	LINear = 0
	NONE = 1


# noinspection SpellCheckingInspection
class IpmMode(Enum):
	"""2 Members, INDividual ... SAME"""
	INDividual = 0
	SAME = 1


# noinspection SpellCheckingInspection
class IpmPlotView(Enum):
	"""2 Members, HISTogram ... TIMeseries"""
	HISTogram = 0
	TIMeseries = 1


# noinspection SpellCheckingInspection
class IpmType(Enum):
	"""10 Members, BINomial ... WAVeform"""
	BINomial = 0
	EQUation = 1
	LIST = 2
	PLUGin = 3
	RANDom = 4
	RLISt = 5
	RSTep = 6
	SHAPe = 7
	STEPs = 8
	WAVeform = 9


# noinspection SpellCheckingInspection
class ItemPattern(Enum):
	"""12 Members, ALT ... ZERO"""
	ALT = 0
	ONE = 1
	R11 = 2
	R13 = 3
	R2A = 4
	R2B = 5
	R3 = 6
	R4A = 7
	R4B = 8
	R5 = 9
	R7 = 10
	ZERO = 11


# noinspection SpellCheckingInspection
class ItemType(Enum):
	"""6 Members, FILLer ... WAVeform"""
	FILLer = 0
	LOOP = 1
	OVL = 2
	PULSe = 3
	SUBSequence = 4
	WAVeform = 5


# noinspection SpellCheckingInspection
class ItemTypeB(Enum):
	"""3 Members, PATTern ... USER"""
	PATTern = 0
	PRBS = 1
	USER = 2


# noinspection SpellCheckingInspection
class Lattice(Enum):
	"""2 Members, RECTangular ... TRIangular"""
	RECTangular = 0
	TRIangular = 1


# noinspection SpellCheckingInspection
class LobesCount(Enum):
	"""2 Members, _2 ... _4"""
	_2 = 0
	_4 = 1


# noinspection SpellCheckingInspection
class LoopType(Enum):
	"""2 Members, FIXed ... VARiable"""
	FIXed = 0
	VARiable = 1


# noinspection SpellCheckingInspection
class LswDirection(Enum):
	"""2 Members, H ... V"""
	H = 0
	V = 1


# noinspection SpellCheckingInspection
class ModuleType(Enum):
	"""3 Members, IPM ... REPort"""
	IPM = 0
	MOP = 1
	REPort = 2


# noinspection SpellCheckingInspection
class MopType(Enum):
	"""21 Members, AM ... QPSK"""
	AM = 0
	AMSTep = 1
	ASK = 2
	BARKer = 3
	BPSK = 4
	CCHiprp = 5
	CHIRp = 6
	FM = 7
	FMSTep = 8
	FSK = 9
	MSK = 10
	NLCHirp = 11
	NOISe = 12
	PCHirp = 13
	PLISt = 14
	PLUGin = 15
	POLYphase = 16
	PSK8 = 17
	PWISechirp = 18
	QAM = 19
	QPSK = 20


# noinspection SpellCheckingInspection
class MovementRframe(Enum):
	"""2 Members, PZ ... WGS"""
	PZ = 0
	WGS = 1


# noinspection SpellCheckingInspection
class MovementRmode(Enum):
	"""3 Members, CYCLic ... ROUNdtrip"""
	CYCLic = 0
	ONEWay = 1
	ROUNdtrip = 2


# noinspection SpellCheckingInspection
class MovementType(Enum):
	"""4 Members, ARC ... WAYPoint"""
	ARC = 0
	LINE = 1
	TRACe = 2
	WAYPoint = 3


# noinspection SpellCheckingInspection
class OutFormat(Enum):
	"""3 Members, ESEQencing ... WV"""
	ESEQencing = 0
	MSW = 1
	WV = 2


# noinspection SpellCheckingInspection
class PhaseMode(Enum):
	"""3 Members, ABSolute ... MEMory"""
	ABSolute = 0
	CONTinuous = 1
	MEMory = 2


# noinspection SpellCheckingInspection
class Pmode(Enum):
	"""2 Members, MOVing ... STATic"""
	MOVing = 0
	STATic = 1


# noinspection SpellCheckingInspection
class PmodeLocation(Enum):
	"""3 Members, MOVing ... STEPs"""
	MOVing = 0
	STATic = 1
	STEPs = 2


# noinspection SpellCheckingInspection
class PmodSource(Enum):
	"""3 Members, EXTernal ... OFF"""
	EXTernal = 0
	INTernal = 1
	OFF = 2


# noinspection SpellCheckingInspection
class PolarCut(Enum):
	"""2 Members, XY ... YZ"""
	XY = 0
	YZ = 1


# noinspection SpellCheckingInspection
class Polarization(Enum):
	"""6 Members, CLEFt ... VERTical"""
	CLEFt = 0
	CRIGht = 1
	HORizontal = 2
	SLEFt = 3
	SRIGht = 4
	VERTical = 5


# noinspection SpellCheckingInspection
class PolarType(Enum):
	"""2 Members, CARTesian ... POLar"""
	CARTesian = 0
	POLar = 1


# noinspection SpellCheckingInspection
class PolynomType(Enum):
	"""5 Members, FRANk ... P4"""
	FRANk = 0
	P1 = 1
	P2 = 2
	P3 = 3
	P4 = 4


# noinspection SpellCheckingInspection
class PrbsType(Enum):
	"""8 Members, P11 ... P9"""
	P11 = 0
	P15 = 1
	P16 = 2
	P20 = 3
	P21 = 4
	P23 = 5
	P7 = 6
	P9 = 7


# noinspection SpellCheckingInspection
class PreviewMode(Enum):
	"""2 Members, ENVelope ... MOP"""
	ENVelope = 0
	MOP = 1


# noinspection SpellCheckingInspection
class PreviewMop(Enum):
	"""3 Members, FREQuency ... PHASe"""
	FREQuency = 0
	IQ = 1
	PHASe = 2


# noinspection SpellCheckingInspection
class ProgramMode(Enum):
	"""3 Members, DEMO ... STANdard"""
	DEMO = 0
	EXPert = 1
	STANdard = 2


# noinspection SpellCheckingInspection
class Psec(Enum):
	"""18 Members, NONE ... SEC9"""
	NONE = 0
	PRIMary = 1
	SEC1 = 2
	SEC10 = 3
	SEC11 = 4
	SEC12 = 5
	SEC13 = 6
	SEC14 = 7
	SEC15 = 8
	SEC16 = 9
	SEC2 = 10
	SEC3 = 11
	SEC4 = 12
	SEC5 = 13
	SEC6 = 14
	SEC7 = 15
	SEC8 = 16
	SEC9 = 17


# noinspection SpellCheckingInspection
class PulseSetting(Enum):
	"""5 Members, GENeral ... TIMing"""
	GENeral = 0
	LEVel = 1
	MKR = 2
	MOP = 3
	TIMing = 4


# noinspection SpellCheckingInspection
class PulseType(Enum):
	"""4 Members, COSine ... SQRT"""
	COSine = 0
	LINear = 1
	RCOSine = 2
	SQRT = 3


# noinspection SpellCheckingInspection
class PwdType(Enum):
	"""4 Members, AMMos ... TEMPlate"""
	AMMos = 0
	DEFault = 1
	PLUGin = 2
	TEMPlate = 3


# noinspection SpellCheckingInspection
class QamType(Enum):
	"""5 Members, Q128 ... Q64"""
	Q128 = 0
	Q16 = 1
	Q256 = 2
	Q32 = 3
	Q64 = 4


# noinspection SpellCheckingInspection
class QpskType(Enum):
	"""6 Members, ASOQpsk ... TGSoqpsk"""
	ASOQpsk = 0
	BSOQpsk = 1
	DQPSk = 2
	NORMal = 3
	OQPSk = 4
	TGSoqpsk = 5


# noinspection SpellCheckingInspection
class RandomDistribution(Enum):
	"""3 Members, NORMal ... UNIForm"""
	NORMal = 0
	U = 1
	UNIForm = 2


# noinspection SpellCheckingInspection
class RasterDirection(Enum):
	"""2 Members, HORizontal ... VERTical"""
	HORizontal = 0
	VERTical = 1


# noinspection SpellCheckingInspection
class RecModel(Enum):
	"""2 Members, INTerfero ... TDOA"""
	INTerfero = 0
	TDOA = 1


# noinspection SpellCheckingInspection
class RepeatMode(Enum):
	"""2 Members, CONTinuous ... SINGle"""
	CONTinuous = 0
	SINGle = 1


# noinspection SpellCheckingInspection
class RepetitionType(Enum):
	"""3 Members, DURation ... VARiable"""
	DURation = 0
	FIXed = 1
	VARiable = 2


# noinspection SpellCheckingInspection
class Rotation(Enum):
	"""2 Members, CCW ... CW"""
	CCW = 0
	CW = 1


# noinspection SpellCheckingInspection
class SanitizeScenario(Enum):
	"""3 Members, ALL ... SCENario"""
	ALL = 0
	REPository = 1
	SCENario = 2


# noinspection SpellCheckingInspection
class ScanType(Enum):
	"""10 Members, CIRCular ... SPIRal"""
	CIRCular = 0
	CONical = 1
	CUSTom = 2
	HELical = 3
	LISSajous = 4
	LSW = 5
	RASTer = 6
	SECTor = 7
	SIN = 8
	SPIRal = 9


# noinspection SpellCheckingInspection
class ScenarioType(Enum):
	"""9 Members, CEMitter ... WAVeform"""
	CEMitter = 0
	CSEQuence = 1
	DF = 2
	DYNamic = 3
	EMITter = 4
	LOCalized = 5
	PDW = 6
	SEQuence = 7
	WAVeform = 8


# noinspection SpellCheckingInspection
class SecurityLevel(Enum):
	"""5 Members, LEV0 ... LEV4"""
	LEV0 = 0
	LEV1 = 1
	LEV2 = 2
	LEV3 = 3
	LEV4 = 4


# noinspection SpellCheckingInspection
class SequenceType(Enum):
	"""2 Members, PULSe ... WAVeform"""
	PULSe = 0
	WAVeform = 1


# noinspection SpellCheckingInspection
class SigCont(Enum):
	"""2 Members, COMM ... PULSe"""
	COMM = 0
	PULSe = 1


# noinspection SpellCheckingInspection
class SourceInt(Enum):
	"""2 Members, EXTernal ... INTernal"""
	EXTernal = 0
	INTernal = 1


# noinspection SpellCheckingInspection
class SourceType(Enum):
	"""2 Members, PROFile ... VARiable"""
	PROFile = 0
	VARiable = 1


# noinspection SpellCheckingInspection
class State(Enum):
	"""2 Members, IDLE ... RUN"""
	IDLE = 0
	RUN = 1


# noinspection SpellCheckingInspection
class TargetOut(Enum):
	"""2 Members, FILE ... INSTrument"""
	FILE = 0
	INSTrument = 1


# noinspection SpellCheckingInspection
class TargetParam(Enum):
	"""20 Members, AMDepth ... WIDTh"""
	AMDepth = 0
	AMFRequency = 1
	CDEViation = 2
	DELay = 3
	DROop = 4
	FALL = 5
	FMDeviation = 6
	FMFRequency = 7
	FREQuency = 8
	FSKDeviation = 9
	LEVel = 10
	OVERshoot = 11
	PHASe = 12
	PRF = 13
	PRI = 14
	RFRequency = 15
	RISE = 16
	RLEVel = 17
	SRATe = 18
	WIDTh = 19


# noinspection SpellCheckingInspection
class TargetType(Enum):
	"""2 Members, PARameter ... VARiable"""
	PARameter = 0
	VARiable = 1


# noinspection SpellCheckingInspection
class TimeMode(Enum):
	"""2 Members, PRF ... PRI"""
	PRF = 0
	PRI = 1


# noinspection SpellCheckingInspection
class TimeReference(Enum):
	"""3 Members, FULL ... VOLTage"""
	FULL = 0
	POWer = 1
	VOLTage = 2


# noinspection SpellCheckingInspection
class Units(Enum):
	"""6 Members, DB ... SEConds"""
	DB = 0
	DEGRees = 1
	HERTz = 2
	NONE = 3
	PERCent = 4
	SEConds = 5


# noinspection SpellCheckingInspection
class Vehicle(Enum):
	"""5 Members, AIRPlane ... STATionary"""
	AIRPlane = 0
	LVEHicle = 1
	RECeiver = 2
	SHIP = 3
	STATionary = 4


# noinspection SpellCheckingInspection
class VehicleMovement(Enum):
	"""6 Members, AIRPlane ... STATionary"""
	AIRPlane = 0
	CAR = 1
	DEFault = 2
	LVEHicle = 3
	SHIP = 4
	STATionary = 5


# noinspection SpellCheckingInspection
class ViewCount(Enum):
	"""8 Members, _100 ... _50000"""
	_100 = 0
	_1000 = 1
	_10000 = 2
	_100000 = 3
	_50 = 4
	_500 = 5
	_5000 = 6
	_50000 = 7


# noinspection SpellCheckingInspection
class ViewXode(Enum):
	"""2 Members, SAMPles ... TIME"""
	SAMPles = 0
	TIME = 1


# noinspection SpellCheckingInspection
class WaveformShape(Enum):
	"""3 Members, RAMP ... TRIangular"""
	RAMP = 0
	SINE = 1
	TRIangular = 2


# noinspection SpellCheckingInspection
class WaveformType(Enum):
	"""10 Members, AIF ... WAVeform"""
	AIF = 0
	APDW = 1
	BEMitter = 2
	CW = 3
	IQDW = 4
	MT = 5
	NOISe = 6
	PDW = 7
	USER = 8
	WAVeform = 9


# noinspection SpellCheckingInspection
class Ymode(Enum):
	"""7 Members, FREQuency ... PHASe"""
	FREQuency = 0
	IQ = 1
	MAGDb = 2
	MAGV = 3
	MAGW = 4
	PAV = 5
	PHASe = 6
