import pyawr.mwoffice as mwo
from pyawr_utils import common_utils
from tkinter import messagebox
import warnings
#
_Elements = common_utils._Elements
_Equations = common_utils._Equations
#
#*****************************************************************************
#
class _Goal():
    def __init__(self, awrde, goal_idx: int, goal_source: str):#------------------------------
        '''
        goal_source: Optimize|Yield
        '''
        self.awrde = awrde
        self._initialize_goal(goal_idx, goal_source)
        #
    def _initialize_goal(self, goal_idx, goal_source):#----------------------------------------
        try:
            if goal_source == 'Optimize':
                self._goal = self.awrde.Project.OptGoals(goal_idx+1)
            elif goal_source == 'Yield':
                self._goal = self.awrde.Project.YieldGoals(goal_idx+1)
            #end if
        except:
            raise RuntimeError('Goal does not exist: ' + goal_name)
        #end try
        self._goal_name = self._goal.Name
        #
    @property
    def goal_name(self) -> str:#-----------------------------------------------------
        return self._goal_name
        #
    @property
    def goal_enabled(self) -> bool:#--------------------------------------------------
        return self._goal.Enable
        #
    @goal_enabled.setter
    def goal_enabled(self, enabled_state:bool):#--------------------------------------------------
        self._goal.Enable = enabled_state
        #
    @property
    def goal_xrange(self) -> tuple:#-----------------------------------------------
        xStart = self._goal.xStart
        xStop = self._goal.xStop
        return (xStart, xStop)
        #
    @goal_xrange.setter
    def goal_xrange(self, xrange_tuple: tuple):#-----------------------------------------------
        if not isinstance(xrange_tuple, tuple):
            raise TypeError('xrange must be tuple: (xStart, xStop)')
        #end if
        try:
            xStart = xrange_tuple[0]
            xStop = xrange_tuple[1]
            self._goal.xStart = xStart
            self._goal.xStop = xStop
        except:
            warnings.warn('goal_xrange could not be set')
        #end try
        #
    @property
    def goal_yrange(self) -> tuple:#-----------------------------------------------
        yStart = self._goal.yStart
        yStop = self._goal.yStop
        return (yStart, yStop)
        #
    @goal_yrange.setter
    def goal_yrange(self, yrange_tuple: tuple):#-----------------------------------------------
        if not isinstance(yrange_tuple, tuple):
            raise TypeError('yrange must be tuple: (yStart, yStop)')
        #end if
        try:
            yStart = yrange_tuple[0]
            yStop = yrange_tuple[1]
            self._goal.yStart = yStart
            self._goal.yStop = yStop
        except:
            warnings.warn('goal_xrange could not be set')
        #end try
        #
    @property
    def goal_type(self) -> str:#--------------------------------------------------------
        '''
        returns the goal type as a string: =, >, or <
        
        The API only allows reading the Type. The API does not allow setting the type.
        The user would need to add a new goal with the desired type and delete the old goal
        
        '''
        goal_type_val = self._goal.Type
        if goal_type_val == 0:
            goal_type_str = '='
        elif goal_type_val == 1:
            goal_type_str = '<'
        elif goal_type_val == 2:
            goal_type_str = '>'
        else:
            warnings.warn('invalid goal type')
            goal_type_str = 'NA'
        #end if
        return goal_type_str
        #
    @property
    def goal_weight(self) -> float:#---------------------------------------------------
        return self._goal.Weight
        #
    @goal_weight.setter
    def goal_weight(self, goal_weight: float):#----------------------------------------
        if (not isinstance(goal_weight, float)) and (not isinstance(goal_weight, int)):
            raise TypeError('goal_weight must be either float or int type')
        #end if
        self._goal.Weight = goal_weight
        #
    @property
    def goal_l_factor(self) -> float:#----------------------------------------------
        return self._goal.LVal
        #
    @goal_l_factor.setter
    def goal_l_factor(self, goal_l_factor: float):#-------------------------------------
        if (not isinstance(goal_l_factor, float)) and (not isinstance(goal_l_factor, int)):
            raise TypeError('goal_l_factor must be either float or int type')
        #end if
        self._goal.LVal = goal_l_factor
        #
    @property
    def goal_cost(self) -> float:#---------------------------------------------------
        return self._goal.Cost
    
#
#*****************************************************************************
#
class _DataFiles():
    '''
    Methods for collection of Data Files in the AWRDE project
    
    Parameters
    ----------
    awrde: The AWRDE object returned from awrde_utils.establish_link()
    
    '''
    def __init__(self, awrde):#----------------------------------------
        self.awrde = awrde
        #
    def _build_data_files_dict(self):#--------------------------------
        '''Create list of all graph names in project
    
        Parameters
        ----------
        None
    
        Returns
        -------
        _data_files_dict: dict
                         keys are the data file names
                         values are the data file objects
        '''        
        self._data_files_dict = {}
        for df in self.awrde.Project.DataFiles:
            data_file = _DataFile(self.awrde, df.Name)
            self._data_files_dict[df.Name] = data_file
        #end for
        #
    @property
    def data_files_dict(self) -> dict:#-----------------------------------------------
        '''return data file dictionary'''
        self._build_data_files_dict()
        return self._data_files_dict
        #
    @property
    def data_file_names_list(self) -> list[str]:#-------------------------------------------
        '''returns list of data file names'''
        data_file_name_list = list()
        for df in self.awrde.Project.DataFiles:
            data_file_name_list.append(df.Name)
        #end for
        return data_file_name_list
        #
    def add_dc_iv_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a DC-IV file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'DC-IV')
        #
    def add_dscr_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a DSCR file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'DSCR')
        #
    def add_gmdif_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a Generalized MDIF file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'GMDIF')
        #
    def add_gmdif_nport_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a Generalized MDIF N-Port file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'GMDIF N-Port')
        #
    def add_mdif_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a MDIF file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'MDIF')
        #
    def add_raw_port_parameters_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a Raw Port Parameters file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'Raw Port Parameters')
        #
    def add_text_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a Text file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'Text')
        #
    def add_touchstone_file(self, data_file_name: str):#-----------------------------------
        '''
        Add a Touchstone file
        
        Parameters
        ----------
        data_file_name: string
        '''
        self._add_data_file(data_file_name, 'Touchstone')
        #
    def remove_data_file(self, data_file_name: str) -> bool:
        '''
        Delete a data file from the AWRDE project
        
        Parameters
        ----------
        data_file_name: string,
                 name of the Data File to be deleted
        
        Returns
        -------
        data_file_removed: bool
                    True if data file successfully deleted,
                    False if data file could not be deleted
                    
        '''        
        if not isinstance(data_file_name, str):
            raise TypeError('data_file_name must be a string type')
        #end if
        data_file_removed = False               
        try:
            for df_idx in range(self.awrde.Project.DataFiles.Count):
                if self.awrde.Project.DataFiles[df_idx].Name == data_file_name:
                    self.awrde.Project.DataFiles.Remove(df_idx+1)
                    data_file_removed = True
                    break
                #end if
            #end for
        except:
            warnings.warn('remove_data_file: Data File ' + data_file_name + ' did not get removed')
        #end for
        return data_file_removed
        #
    def rename_data_file(self, data_file_name: str, new_data_file_name: str):#--------------------
        '''
        rename Data File
    
        Parameters
        ----------
        data_file_name: string
                         existing graph name
        new_data_file_name: string
                         new graph name
        '''        
        if not isinstance(data_file_name, str):
            raise TypeError('data_file_name must be a string')
        #end if
        if not isinstance(new_data_file_name, str):
            raise TypeError('new_data_file_name must be a string')
        #end if
        data_file_name_list = self.data_file_names_list
        found_it = False
        for data_file_name_from_list in data_file_name_list:
            if data_file_name_from_list == data_file_name:
                found_it = True
                if new_data_file_name in data_file_name_list:
                    YesNo = messagebox.askyesno('Rename Data File','Data File '\
                        + new_data_file_name + ' exists. Remove existing Data File ?')
                    if YesNo:
                        self.remove_data_file(new_data_file_name)
                    else:
                        new_data_file_name += ' 1'
                    #end if
                #end if
                try:
                    df = self.awrde.Project.DataFiles(data_file_name)
                    df.Name = new_data_file_name
                except:
                    raise RuntimeError('problem with renaming data file')
                #end try
            #end if
        #end for
        if not found_it:
            warnings.warn('data file rename failed: ' + data_file_name)
        #end if
        #
    def copy_data_file(self, data_file_name: str, new_data_file_name: str):#-----------------------
        '''
        copy Data File
    
        Parameters
        ----------
        data_file_name: string
                         existing data file name
        new_data_file_name: string
                         new data file name
        '''
        if not isinstance(data_file_name, str):
            raise TypeError('data_file_name must be a string')
        #end if
        if not isinstance(new_data_file_name, str):
            raise TypeError('new_data)file_name must be a string')
        #end if        
        for df in self.awrde.Project.DataFiles:
            if df.Name == new_data_file_name:
                new_data_file_name = new_data_file_name + ' 1'
            #end if
        #end for
        #
        try:
            for df_idx in range(1, self.awrde.Project.DataFiles.Count+1):
                df = self.awrde.Project.DataFiles(df_idx)
                if df.Name == data_file_name:
                    self.awrde.Project.DataFiles.Copy(df_idx, new_data_file_name)
                #end if
            #end for
        except:
            raise RuntimeError('problem with copying data file')
        #end try
        #
    def import_data_file(self, data_file_name: str, file_path: str, data_file_type: str):#------
        '''
        import data file
        
        Parameters
        ----------
        data_file_name: string
               name of the data file as it will appear in the project
               
        file_path: string
               full directory and file name of the file to be imported
               
        data_file_type: string
               valid values:
                    DC-IV File
                    DSCR File
                    Generalized MDIF Data File
                    Generalized MDIF N-Port File
                    MDIF File
                    Raw Port Parameters File
                    Text File
                    Touchstone File
        '''
        if not isinstance(data_file_name, str):
            raise TypeError('data_file_name must be string type')
        #end if
        if not isinstance(file_path, str):
            raise TypeError('file_path must be string type')
        #end if
        if not isinstance(data_file_type, str):
            raise TypeError('data_file_type must be string type')
        #end if
        #
        if data_file_type == 'DC-IV File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_IV
        elif data_file_type == 'DSCR File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_DSCR
        elif data_file_type == 'Generalized MDIF Data File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_GMDIF
        elif data_file_type == 'Generalized MDIF N-Port File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_GMDIFD
        elif data_file_type == 'MDIF File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_MDIF
        elif data_file_type == 'Raw Port Parameters File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_RAW
        elif data_file_type == 'Text File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_TXT
        elif data_file_type == 'Touchstone File':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_SNP
        else:
            raise RuntimeError('data_file_type not recognized: ' + data_file_type)
        #end if
        if self._does_data_file_exist(data_file_name):
            YesNo = messagebox.askyesno('Import Data File','Data File ' + data_file_name + ' exists. Delete existing Data File?')
            if YesNo:
                self.remove_data_file(data_file_name)
            #end if
        #end if
        try:
            self.awrde.Project.DataFiles.Import(data_file_name, file_path, data_file_type_enum)
        except:
            raise RuntimeError('Problem with importing data file')
        #end try
        #
    def _does_data_file_exist(self, data_file_name: str) -> bool:#------------------------
        data_file_exists = False
        for df in self.awrde.Project.DataFiles:
            if df.Name == data_file_name:
                data_file_exists = True
            #end if
        #end for
        return data_file_exists
        #
    def _add_data_file(self, data_file_name, data_file_type):#----------------------------
        if data_file_type == 'DC-IV':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_IV
        elif data_file_type == 'DSCR':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_DSCR
        elif data_file_type == 'GMDIF':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_GMDIF
        elif data_file_type == 'GMDIF N-Port':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_GMDIFD
        elif data_file_type == 'MDIF':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_MDIF
        elif data_file_type == 'Raw Port Parameters':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_RAW
        elif data_file_type == 'Text':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_TXT
        elif data_file_type == 'Touchstone':
            data_file_type_enum = mwo.mwDataFileType.mwDFT_SNP
        #end if
        if self._does_data_file_exist(data_file_name):
            YesNo = messagebox.askyesno('Add Data File','Data File ' + data_file_name + ' exists. Delete existing Data File?')
            if YesNo:
                self.remove_data_file(data_file_name)
            else:
                data_file_name += ' 1'
            #end if
        #end if
        try:
            self.awrde.Project.DataFiles.AddNew(data_file_name, data_file_type_enum)
        except:
            warnings.warn('Data File not added. Possible name conflict')
        #end try
#
#*****************************************************************************
#
class _DataFile():
    def __init__(self, awrde, data_file_name: str):#-----------------------------------
        self.awrde = awrde
        self._initialize_data_file(data_file_name)
        #
    def _initialize_data_file(self, data_file_name: str):#-------------------------------------
        try:
            self._df = self.awrde.Project.DataFiles(data_file_name)
        except:
            raise RuntimeError('Data File does not exist: ' + data_file_name)
        #end try
        #
    @property
    def data_file_name(self) -> str:#------------------------------------------------------
        '''Returns name of the Data File'''
        return self._df.Name
        #
    @property
    def data_file_type(self) -> str:#--------------------------------------------------
        '''
        Reports data file type 
        
        Returns
        -------
        data_file_type_str: string
              DC-IV File, DSCR File, Generalized MDIF Data File, Generalized MDIF N-Port File,
              MDIF File, Raw Port Parameters File, Text File, Touchstone File
        
        ''' 
        data_file_type_enum = self._df.Type
        if mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_IV:
            data_file_type_str = 'DC-IV File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_DSCR:
            data_file_type_str = 'DSCR File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_GMDIF:
            data_file_type_str = 'Generalized MDIF Data File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_GMDIFD:
            data_file_type_str = 'Generalized MDIF N-Port File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_MDIF:
            data_file_type_str = 'MDIF File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_RAW:
            data_file_type_str = 'Raw Port Parameters File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_TXT:
            data_file_type_str = 'Text File'
        elif mwo.mwDataFileType(data_file_type_enum) == mwo.mwDataFileType.mwDFT_SNP:
            data_file_type_str = 'Touchstone File'
        #end if
        return data_file_type_str
        #
    def export_data_file(self, file_path: str) -> bool:#--------------------------------------
        '''
        exports the data file to the directory and name specified by file_path
        
        Parameters
        ----------
        file_path: string
              full director and file name
        
        Returns
        -------
        export_successful: bool
        '''
        if not isinstance(file_path,str):
            raise TypeError('file_path must be string type')
        #end if
        #
        export_successful = True
        try:
            self._df.Export(file_path)
        except:
            export_successful = False
        #end try
        return export_successful
        
#
#*****************************************************************************
#
class _Optimization():
    '''
    methods for using the Optimizer
    Includes: setting/modifying goals
              modifying optimization variables
              setting optimizer
              running optimizer
    
    '''
    def __init__(self, awrde):#--------------------------------------------------------
        self.awrde = awrde
        #
    @property
    def optimization_variables_dict(self) -> dict:#-----------------------------------
        '''
        Returns dictionary of variables that are setup for optimization
        
        Returns
        -------
        optimization_variables_dict: dictionary
            Keys: Index
            Values: Dictionary of fields:
                        Document Name
                        Document Type: Schematic, System Diagram, EM Structure, Global Definition
                        Element Type: Element or Equation
                        Element Name
                        Variable Name
                        Nominal Value
                        Constrained: True or False
                        Lower Constraint
                        Upper Constraint
                        Step Size
            
        '''
        optimization_variables_dict = {}
        opt_dict_idx = 0
        Documents_dict = {0:self.awrde.Project.Schematics,
                          1:self.awrde.Project.SystemDiagrams,
                          2:self.awrde.Project.GlobalDefinitionDocuments,
                          3:self.awrde.Project.EMStructures}
        DocType_dict = {0:'Circuit Schematic', 1:'System Diagram', 2:'Global Definitions',
                        3:'EM Structure'}
        NumDocuments = len(Documents_dict)
        #
        for doc_idx in range(NumDocuments):
            Documents = Documents_dict[doc_idx]
            for document in Documents:
                if DocType_dict[doc_idx] == 'Global Definitions':
                    Elements_object = document.DataElements
                    Equations_object = document.Equations
                elif DocType_dict[doc_idx] == 'EM Structure':
                    Elements_object = document.Schematic.Elements
                    Equations_object = document.Schematic.Equations
                else:
                    Elements_object = document.Elements
                    Equations_object = document.Equations
                #end if
                for element in Elements_object:
                    for param in element.Parameters:
                        if param.Optimize:
                            Fields_dict = {}
                            Fields_dict['Document Name'] = document.Name
                            Fields_dict['Document Type'] = DocType_dict[doc_idx]
                            Fields_dict['Element Type'] = 'Element'
                            Fields_dict['Variable Name'] = element.Name + ' : '+param.Name
                            Fields_dict['Constrained'] = param.Constrain
                            Fields_dict['Nominal Value'] = param.ValueAsDouble
                            Fields_dict['Lower Constraint'] = param.LowerConstraint
                            Fields_dict['Upper Constraint'] = param.UpperConstraint
                            Fields_dict['Step Size'] = param.StepSize
                            optimization_variables_dict[opt_dict_idx] = Fields_dict
                            opt_dict_idx += 1
                        #end if
                    #end for
                #end for
                for eqn in Equations_object:
                    if eqn.Optimize:
                        Fields_dict = {}
                        Fields_dict['Document Name'] = document.Name
                        Fields_dict['Document Type'] = DocType_dict[doc_idx]
                        Fields_dict['Element Type'] = 'Equation'
                        Expression = eqn.Expression
                        Expression = Expression.lstrip()
                        Expression = Expression.rstrip()
                        Fields_dict['Variable Name'] = Expression
                        Fields_dict['Constrained'] = eqn.Constrain
                        try:
                            val_str = eqn.Expression.split('=')
                            val = float(val_str[1])
                        except:
                            val = 'NA'
                        #end try
                        Fields_dict['Nominal Value'] = val
                        Fields_dict['Lower Constraint'] = eqn.LowerConstraint
                        Fields_dict['Upper Constraint'] = eqn.UpperConstraint
                        Fields_dict['Step Size'] = eqn.StepSize
                        optimization_variables_dict[opt_dict_idx] = Fields_dict
                        opt_dict_idx += 1
                    #end if
                #end for
            #end for
        #end for
        return optimization_variables_dict
        #
    def print_optimization_variables(self, optimization_variables_dict:dict):#----------------
        '''prints the optimization variables and their attributes'''
        NumOptVars = len(optimization_variables_dict)
        ov = optimization_variables_dict
        for opt_idx in range(NumOptVars):
            print('{:s}{:3.0f}'.format('Optimization Variable Index =',opt_idx))
            print('    {:s} {:s}'.format('Document Name =',ov[opt_idx]['Document Name']))
            print('    {:s} {:s}'.format('Document Type =',ov[opt_idx]['Document Type']))
            print('    {:s} {:s}'.format('Element Type =',ov[opt_idx]['Element Type']))
            if ov[opt_idx]['Element Type'] == 'Element':
                print('    {:s} {:s}'.format('Element Name : Parameter Name =',ov[opt_idx]['Variable Name']))
            elif ov[opt_idx]['Element Type'] == 'Equation':
                print('    {:s}{:s}{:s}'.format('Expression = "',ov[opt_idx]['Variable Name'],'"'))
            #end if
            print('    {:s} {:s}'.format('Constrained =',str(ov[opt_idx]['Constrained'])))
            print('    {:s} {:s}'.format('Nominal Value =',str(ov[opt_idx]['Nominal Value'])))
            print('    {:s} {:s}'.format('Lower Constraint =',str(ov[opt_idx]['Lower Constraint'])))
            print('    {:s} {:s}'.format('Upper Constraint =',str(ov[opt_idx]['Upper Constraint'])))
            print('    {:s} {:s}'.format('Step Size =',str(ov[opt_idx]['Step Size'])))
            print('')
        #end for
        #
    @property
    def optimization_goals_dict(self) -> dict:#------------------------------------------
        '''
        returns dictionary of optimizer goals
        
        Returns
        -------
        optimization_goals_dict: dictionary
             Keys: Index
             Values: Dictionary of fields
                        
        
        '''
        self._build_opt_goal_dict()
        return self._optimization_goals_dict
        #
    def add_optimization_goal(self, measurement_name:str, goal_type:str, goal_xrange:tuple,
                              goal_yrange:tuple, goal_weight:float, goal_l_factor:float):
        '''
        add optimization goal to project
        
        Parameters
        ----------
           measurement_name : string   The measurement name in form of doc name : measurmeent
           goal_type : string  '>', '<', or '='
           Xrage : tuple  (xStart, xStop)  must be in base units
           Yrange : tuple (yStart, yStop)  
           
        '''
        if not isinstance(measurement_name, str):
            raise TypeError('measurement_name must be a string')
        if not isinstance(goal_type, str):
            raise TypeError('goal_type must be a string')
        if not isinstance(goal_yrange, tuple):
            raise TypeError('goal_xrange must be a tuple')
        if not isinstance(goal_yrange,tuple):
            raise TypeError('goal_yrange must be a tuple')
        if (not isinstance(goal_weight, float)) and (not isinstance(goal_weight, int)):
            raise TypeError('goal_weight must be either float or int type')        
        if (not isinstance(goal_l_factor, float)) and (not isinstance(goal_l_factor, int)):
            raise TypeError('goal_weight must be either float or int type')        
        #end if
        #
        if goal_type not in {'<','>','='}:
            raise RuntimeError('invalid goal_type: ' + goal_type)
        #end if
        #
        meas_name_split = measurement_name.split(':')
        CircuitName = meas_name_split[0]
        MeasName = meas_name_split[1]
        if goal_type == '=':
            GoalTypeEnum = 0
        elif goal_type == '<':
            GoalTypeEnum = 1
        elif goal_type == '>':
            GoalTypeEnum = 2
        else:
            raise RuntimeError('invalid goal_type: ' + goal_type)
        #end if
        xStart = goal_xrange[0]
        xStop = goal_xrange[1]
        yStart = goal_yrange[0]
        yStop = goal_yrange[1]
        xUnit = 0
        yUnit = 0
        #
        try:
            goal_idx = self.awrde.Project.OptGoals.Count
            self.awrde.Project.OptGoals.AddGoal(CircuitName, MeasName, GoalTypeEnum, goal_weight,
                                        goal_l_factor, xStart, xStop, xUnit, yStart, yStop, yUnit)
            self._optimization_goals_dict[goal_idx] = _Goal(self.awrde, goal_idx, 'Optimize')
        except:
            warnings.warn('optimization goal could not be added')
        #end try
        #
    def remove_optimization_goal(self, optimization_goal_name:str):#------------------------------
        '''
        Remove optimiztion goal
        '''
        if not isinstance(optimization_goal_name, str):
            raise TypeError('optimization_goal_name must be string type')
        #end if
        opt_goal_removed = False
        #
        for i in range(len(self._optimization_goals_dict)):
            temp_opt_goal = self._optimization_goals_dict[i]
            if optimization_goal_name == temp_opt_goal.goal_name:
                dict_idx = i
                break
            #end if
        #end for
        #
        for opt_goal_idx in range(1, self.awrde.Project.OptGoals.Count+1):
            temp_opt_goal_name = self.awrde.Project.OptGoals(opt_goal_idx).Name
            if temp_opt_goal_name == optimization_goal_name:
                self.awrde.Project.OptGoals.Remove(opt_goal_idx)
                opt_goal_removed = True
                self._optimization_goals_dict.pop(dict_idx)
                break
            #end if
        #end for
        if not opt_goal_removed:
            warnings.warn('Optimization Goal ' + optimization_goal_name + ' did not get removed')
        #end for
        return opt_goal_removed
        #
    @property
    def total_opt_goal_cost(self) -> float:#---------------------------------------------------
        '''returns total cost of the all the combined goals'''
        return self.awrde.Project.OptGoals.TotalCost
        #
    @property
    def optimization_type_dict(self) -> list:#-----------------------------------------------
        '''
        returns dictionary of all the avialble optimization methods
        
        Returns
        -------
        opt_typ_dict: dictionary
                      keys are index which corresponds to Optimizer.Type
                      values are the names of the optimizer types
        
        '''
        opt_type_dict = {}
        for i in range(1, self.awrde.Project.Optimizer.TypeCount+1):
            opt_type_dict[i] = self.awrde.Project.Optimizer.TypeName(i)
        #end for
        return opt_type_dict
        #
    @property
    def optimization_type(self) -> str: #-----------------------------------------------
        '''
        returns optimization type name
        '''
        TypeNum = self.awrde.Project.Optimizer.Type
        self._build_opt_properties_dict()  #build the properties dictionary upon querry of the optimization type
        return self.awrde.Project.Optimizer.TypeName(TypeNum)
        #
    @optimization_type.setter
    def optimization_type(self, optimzation_type_name: str):#---------------------------
        '''sets the current optimization type'''
        if not isinstance(optimzation_type_name, str):
            raise TypeError('optimization_type_name must be a string')
        #end if
        found_it = False
        for i in range(1, self.awrde.Project.Optimizer.TypeCount+1):
            if optimzation_type_name == self.awrde.Project.Optimizer.TypeName(i):
                found_it = True
                break
            #end if
        #end for
        if not found_it:
            raise RuntimeError('Invalid optimization type: '+optimzation_type_name)
        #end if
        self.awrde.Project.Optimizer.Type = i
        self._build_opt_properties_dict() #Update the optimization properties dictionary upon changing the optimization type
        #
    @property
    def optimization_type_properties(self) -> dict:#-------------------------------------------
        '''
        returns a dictionary of properties for the current optimization type
        
        Returns
        -------
        opt_properties_dict: dictionary
                             keys are the property name
                             values are the property values
        '''
        try:
            opt_properties_dict = self._opt_properties_dict
        except:
            self._build_opt_properties_dict()
            opt_properties_dict = self._opt_properties_dict
        #end try
        return opt_properties_dict
        #
    def optimization_update_type_properties(self):#----------------------------------------------
        '''update the optimization type properties'''
        try:
            for prop in self.awrde.Project.Optimizer.Properties:
                prop.Value = self._opt_properties_dict[prop.Name]
            #end for
        except:
            warnings.warn('Optimization properties not updated')
        #end try
        #
    @property
    def optimization_max_iterations(self) -> float:#------------------------------------------
        ''' returns the Optimizer MaxIterations'''
        return self.awrde.Project.Optimizer.MaxIterations
        #
    @optimization_max_iterations.setter
    def optimization_max_iterations(self, max_iterations: float):#---------------------------
        '''sets the Optimizer MaxIterations'''
        if (not isinstance(max_iterations, float)) and (not isinstance(max_iterations, int)):
            raise TypeError('max_iterations must be either a float or int type')
        #end if
        #
        try:
            self.awrde.Project.Optimizer.MaxIterations = max_iterations
        except:
            warnings.warn('Optimizer max iterations could not be set')
        #end try
        self.awrde.Project.Optimizer.MaxIterations = int(max_iterations)
        #
    @property
    def optimization_show_all_iterations(self) -> bool:#---------------------------------------------
        return self.awrde.Project.Optimizer.ShowAllUpdates
        #
    @optimization_show_all_iterations.setter
    def optimization_show_all_iterations(self, show_all_iterations: bool):#----------------------
        if not isinstance(show_all_iterations, bool):
            raise TypeError('show_all_iterations must be boolean type')
        #end if
        self.awrde.Project.Optimizer.ShowAllUpdates = show_all_iterations
        #
    @property
    def optimization_stop_at_minimum_error(self) -> bool:#---------------------------------------------
        return self.awrde.Project.Optimizer.StopAtMin
        #
    @optimization_stop_at_minimum_error.setter
    def optimization_stop_at_minimum_error(self, stop_at_min_error: bool):#----------------------
        if not isinstance(stop_at_min_error, bool):
            raise TypeError('stop_at_min_error must be boolean type')
        #end if
        self.awrde.Project.Optimizer.StopAtMin = stop_at_min_error
        #
    @property
    def optimization_stop_on_simulation_error(self) -> bool:#---------------------------------------------
        return self.awrde.Project.Optimizer.StopOnErr
        #
    @optimization_stop_on_simulation_error.setter
    def optimization_stop_on_simulation_error(self, stop_on_sim_error: bool):#----------------------
        if not isinstance(stop_on_sim_error, bool):
            raise TypeError('stop_on_sim_error must be boolean type')
        #end if
        self.awrde.Project.Optimizer.StopOnErr = stop_on_sim_error
        #
    @property
    def optimization_cancel_on_stop_request(self) -> bool:#---------------------------------------------
        return self.awrde.Project.Optimizer.CancelOnStop
        #
    @optimization_cancel_on_stop_request.setter
    def optimization_cancel_on_stop_request(self, cancel_on_stop_request: bool):#----------------------
        if not isinstance(cancel_on_stop_request, bool):
            raise TypeError('cancel_on_stop_request must be boolean type')
        #end if
        self.awrde.Project.Optimizer.CancelOnStop = cancel_on_stop_request
        #
    @property
    def optimization_log_to_file(self) -> bool:#---------------------------------------------
        return self.awrde.Project.Optimizer.LogToFile
        #
    @optimization_log_to_file.setter
    def optimization_log_to_file(self, log_to_file: bool):#----------------------
        if not isinstance(log_to_file, bool):
            raise TypeError('log_to_file must be boolean type')
        #end if
        self.awrde.Project.Optimizer.LogToFile = log_to_file
        #    
    @property
    def optimization_cost(self) -> float:#-----------------------------------------------------
        return self.awrde.Project.Optimizer.Cost
        #
    @property
    def optimization_best_cost(self) -> float:#-----------------------------------------------------
        return self.awrde.Project.Optimizer.BestCost
        #
    @property
    def optimization_current_iteration(self) -> int:#---------------------------------------------
        return self.awrde.Project.Iterataion
        #
    @property
    def optimization_start(self) -> bool:#---------------------------------------------------------
        return self.awrde.Project.Optimizer.Running
        #
    @optimization_start.setter
    def optimization_start(self, opt_start: bool):#----------------------------------------
        if not isinstance(opt_start, bool):
            raise TypeError('opt_start must be boolean type')
        #end if
        self.awrde.Project.Optimizer.Running = opt_start
        #
    def optimization_reset(self):#----------------------------------------------------------
        self.awrde.Project.Optimizer.Reset()
        #
    def optimization_round(self, num_significant_digits: int):#---------------------------------
        if not isinstance(num_significant_digits, int):
            raise TypeError('num_significant_digits must be int type')
        #end if
        self.awrde.Project.Optimizer.Round(num_significant_digits, True, True)
        #
    def _build_opt_goal_dict(self) -> dict:#---------------------------------------------------
        self._optimization_goals_dict = {}
        for goal_idx in range(self.awrde.Project.OptGoals.Count):
            self._optimization_goals_dict[goal_idx] = _Goal(self.awrde, goal_idx, 'Optimize')
        #end for
        #        
    def _build_opt_properties_dict(self) -> dict:#--------------------------------------------
        ''' builds a dictionary of optimization properties '''
        self._opt_properties_dict = {}
        for prop in self.awrde.Project.Optimizer.Properties:
            self._opt_properties_dict[prop.Name] = prop.Value
        #end for
        #
#
#*****************************************************************************
#
class _GlobalDefinitions():
    '''
    Methods for collection of Global Definitions Documents
    
     Parameters
    ----------
    awrde: The AWRDE object returned from awrde_utils.establish_link()
    '''
    def __init__(self, awrde):#----------------------------------------
        self.awrde = awrde
        #
    def _build_global_defs_dict(self):#--------------------------------
        '''Create list of all graph names in project
    
        Parameters
        ----------
        None
    
        Returns
        -------
        _gloabal_defs_dict: dict
                            keys are the names of the global definitions documents
                            values are the global definition document objects
        '''
        self._global_defs_dict = {}
        for gd in self.awrde.Project.GlobalDefinitionDocuments:
            global_def = _GlobalDefinition(self.awrde, gd.Name)
            self._global_defs_dict[gd.Name] = global_def
        #end for
        #
    @property
    def global_definitions_dict(self) -> dict:#-------------------------------------
        '''returns global definition documents dictionary'''
        self._build_global_defs_dict()
        return self._global_defs_dict
        #
    @property
    def global_definitions_list(self) -> list:#-----------------------------------
        '''returns global definition documents list of names'''
        gloabal_defs_list = list()
        for gd in self.awrde.Project.GlobalDefinitionDocuments:
            gloabal_defs_list.append(gd.Name)
        #end for
        return gloabal_defs_list
        #
    def add_global_definitions_document(self, global_def_doc_name: str):#-----------------------------------
        gd_doc_exists = False
        for gd in self.awrde.Project.GlobalDefinitionDocuments:
            if gd.Name == global_def_doc_name:
                gd_doc_exists = True
            #end if
        #end for
        if gd_doc_exists:
            YesNo = messagebox.askyesno('Add Global Definition Document','Global Definition Document ' + global_def_doc_name + ' exists. Delete existing Global Definion Document?')
            if YesNo:
                self.remove_global_definitions_document(global_def_doc_name)
            else:
                global_def_doc_name += ' 1'
            #end if
        #end if
        try:
            self.awrde.Project.GlobalDefinitionDocuments.Add(global_def_doc_name)
        except:
            warnings.warn('Global definition doc not added. Possible name conflict')
        #end try
        #
    def remove_global_definitions_document(self, global_def_doc_name: str) -> bool:#-----------------
        '''
        Delete a global definition document from the AWRDE project
        
        Parameters
        ----------
        global_def_doc_name: string,
                 name of the Global Definition Document  to be deleted
        
        Returns
        -------
        global_def_doc_removed: bool
                    True if global definition document successfully deleted,
                    False if global definition document could not be deleted
                    
        '''             
        if not isinstance(global_def_doc_name, str):
            raise TypeError('global_def_doc_name must be a string type')
        #end if
        global_def_doc_removed = False
        try:
            for gd_idx in range(self.awrde.Project.GlobalDefinitionDocuments.Count):
                print(self.awrde.Project.GlobalDefinitionDocuments[gd_idx].Name,'    ',global_def_doc_name)
                if self.awrde.Project.GlobalDefinitionDocuments[gd_idx].Name == global_def_doc_name:
                    self.awrde.Project.GlobalDefinitionDocuments.Remove(gd_idx+1)
                    global_def_doc_removed = True
                    break
                #end if
            #end for
        except:
            warnings.warn('remove_global_definitions_document: Global Definitions Document ' + global_def_doc_name + ' did not get removed')
        #end try
        return global_def_doc_removed
        #
#
#*****************************************************************************
#
class _GlobalDefinition(_Elements, _Equations):
    def __init__(self, awrde, global_def_name: str):#-----------------------------------
        self.awrde = awrde
        self._initialize_data_file(global_def_name)
        #
    def _initialize_data_file(self, global_def_name: str):#-------------------------------------
        try:
            self._gd = self.awrde.Project.GlobalDefinitionDocuments(global_def_name)
        except:
            raise RuntimeError('Global Definition Document does not exist: ' + global_def_name)
        #end try
        _Elements.__init__(self, self._gd, 'Global Definition')
        _Equations.__init__(self, self._gd)        
        #
    @property
    def global_def_name(self) -> str:#------------------------------------------------------
        '''Returns name of the Global Defintion Document'''
        return self._gd.Name
        #    
#
#*****************************************************************************
#