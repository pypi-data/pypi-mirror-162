import math
import pandas as pd

from steam_sdk.data import DataModelMagnet as dM
from steam_sdk.data import DataRoxieParser as dR
from steam_sdk.data import DataFiQuS as dF


class BuilderFiQuS:
    """
        Class to generate FiQuS models
    """

    def __init__(self,
                 input_model_data: dM.DataModelMagnet = None,
                 input_roxie_data: dR.RoxieData = None,
                 local_model_path: str = None,
                 flag_build: bool = True,
                 flag_plot_all: bool = False,
                 verbose: bool = True):
        """
            Object is initialized by defining FiQuS variable structure and file template.
            If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.flag_plot_all: bool = flag_plot_all
        self.local_folder: str = local_model_path
        self.model_data: dM.DataModelMagnet = input_model_data
        self.roxie_data: dR.RoxieData = input_roxie_data

        if not self.model_data and flag_build:
            raise Exception('Cannot build model instantly without providing DataModelMagnet')

        # Data structure
        if self.model_data:  # to avoid errors during library import
            self.data_FiQuS = dF.DataFiQuS()
            self.data_FiQuS.general.magnet_name = self.model_data.GeneralParameters.magnet_name
            self.data_FiQuS.general.magnet_type = self.model_data.GeneralParameters.magnet_type

            if self.model_data.GeneralParameters.magnet_type == 'multipole':
                self.data_FiQuS_geo = dF.FiQuSGeometry()
                self.data_FiQuS_set = dF.FiQuSSettings()
                if flag_build:
                    self.buildDataMultipole()

            elif self.model_data.GeneralParameters.magnet_type == 'CCT':
                if flag_build:
                    self.buildDataCCT()

            else:
                raise Exception('Incompatible magnet type.')

    def buildDataCCT(self):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """
        self.data_FiQuS.cct.geometry = self.model_data.Options_FiQuS.cct.geometry
        self.data_FiQuS.cct.mesh = self.model_data.Options_FiQuS.cct.mesh
        self.data_FiQuS.cct.solve = self.model_data.Options_FiQuS.cct.solve
        self.data_FiQuS.cct.postproc = self.model_data.Options_FiQuS.cct.postproc
        self.data_FiQuS.cct.steps = self.model_data.Options_FiQuS.cct.steps

    def buildDataMultipole(self):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """
        # geom file
        self.data_FiQuS_geo.Roxie_Data = dR.RoxieData(**self.roxie_data.dict())

        # set file
        self.data_FiQuS_set.Model_Data_GS.general_parameters.I_ref =\
            [self.model_data.Options_LEDET.field_map_files.Iref] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        for cond in self.model_data.Conductors:
            if cond.cable.type == 'Rutherford':
                self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] =\
                    dF.ConductorFiQuS(cable=dF.RutherfordFiQuS(type=cond.cable.type))
            elif cond.cable.type == 'Ribbon':
                self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] =\
                    dF.ConductorFiQuS(cable=dF.RibbonFiQuS(type=cond.cable.type))
            conductor = self.data_FiQuS_set.Model_Data_GS.conductors[cond.name]
            conductor.cable.bare_cable_width = cond.cable.bare_cable_width
            conductor.cable.bare_cable_height_mean = cond.cable.bare_cable_height_mean

        # yaml file
        self.data_FiQuS.multipole.options = self.model_data.Options_FiQuS.multipole.options
        self.data_FiQuS.multipole.options.plot_all = self.flag_plot_all
        if self.local_folder:
            self.data_FiQuS.multipole.options.output_folder = self.local_folder

        self.data_FiQuS.multipole.mesh = self.model_data.Options_FiQuS.multipole.mesh

        self.data_FiQuS.multipole.solve.I_initial = \
            [self.model_data.Power_Supply.I_initial] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        self.data_FiQuS.multipole.solve.pro_template = self.model_data.Options_FiQuS.multipole.solve.pro_template

        self.data_FiQuS.multipole.post_proc = self.model_data.Options_FiQuS.multipole.post_proc
