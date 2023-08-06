from pydantic import BaseModel
from typing import (Dict, List, Union, Literal)
from steam_sdk.data.DataRoxieParser import RoxieData
from steam_sdk.data.DataModelMagnet import GeometryCCT
from steam_sdk.data.DataModelMagnet import MeshCCT
from steam_sdk.data.DataModelMagnet import SolveCCT
from steam_sdk.data.DataModelMagnet import PostprocCCT
from steam_sdk.data.DataModelMagnet import Steps
from steam_sdk.data.DataModelMagnet import OptionMultipole
from steam_sdk.data.DataModelMagnet import MeshMultipole
from steam_sdk.data.DataModelMagnet import PostProcMultipole


class RibbonFiQuS(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Ribbon']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class RutherfordFiQuS(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Rutherford']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class ConductorFiQuS(BaseModel):
    """
        Class for conductor type
    """
    cable: Union[RutherfordFiQuS, RibbonFiQuS] = {'type': 'Rutherford'}


class GeneralSetting(BaseModel):
    """
        Class for general information on the case study
    """
    I_ref: List[float] = None


class ModelDataSetting(BaseModel):
    """
        Class for model data
    """
    general_parameters: GeneralSetting = GeneralSetting()
    conductors: Dict[str, ConductorFiQuS] = {}


class FiQuSSettings(BaseModel):
    """
        Class for FiQuS multipole settings (.set)
    """
    Model_Data_GS: ModelDataSetting = ModelDataSetting()


class FiQuSGeometry(BaseModel):
    """
        Class for FiQuS multipole Roxie data (.geom)
    """
    Roxie_Data: RoxieData = RoxieData()


# Modified classes with respect to Options_FiQuS.multipole
class SolveMultipoleFiQuS(BaseModel):
    I_initial: List[float] = None
    pro_template: str = None  # file name of .pro template file
############################


class MPDM(BaseModel):
    """
        Class for FiQuS multipole
    """
    options: OptionMultipole = OptionMultipole()
    mesh: MeshMultipole = MeshMultipole()
    solve: SolveMultipoleFiQuS = SolveMultipoleFiQuS()
    post_proc: PostProcMultipole = PostProcMultipole()


# Modified classes with respect to Options_FiQuS.cct

############################


class CCTDM(BaseModel):
    """
        Class for FiQuS CCT
    """
    geometry: GeometryCCT = GeometryCCT()
    mesh: MeshCCT = MeshCCT()
    solve: SolveCCT = SolveCCT()
    postproc: PostprocCCT = PostprocCCT()
    steps: Steps = Steps()


class GeneralFiQuS(BaseModel):
    """
        Class for FiQuS general
    """
    magnet_name: str = None
    magnet_type: str = None


class DataFiQuS(BaseModel):
    """
        Class for FiQuS
    """
    general: GeneralFiQuS = GeneralFiQuS()
    cct: CCTDM = CCTDM()
    multipole: MPDM = MPDM()


