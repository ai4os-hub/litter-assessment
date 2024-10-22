import yaml
import os
import numpy as np
import pandas as pd

class results_df:
    def __init__(self, result, type, gsd=0.2):
        self.gsd = gsd
        self.type = type
        self.c_matrix = result.c_matrix
        self.alt_correct = self.get_altcorrection()
        self.df = []

    def load_configs(self):
        wd = os.getcwd()
        path = os.path.join(wd, 'litter-assessment/litter_assessment_service/configs.yaml')
        if not os.path.exists(path):
            path = os.path.join(wd, 'litter_assessment_service/configs.yaml')
        with open(path, 'rb') as f:
            params = yaml.safe_load(f)
            label = params['label'][f'label {self.type}']
            correction_params = params['correction parameters'][f'params_{self.type}']
        return label, correction_params
    
    def get_altcorrection(self):
        norm_GSD = 0.2 # cm/px 
        alt_correction = self.gsd**2 / norm_GSD**2
        return alt_correction

class PLD_df(results_df):
    def __init__(self, *args):
        super().__init__(*args)

        self.dense_few = [3.5, 1,5]
    
    def get_dataframe(self):
        label, _ = self.load_configs()
        label = label + ['Litter abundances','Litter m²','Litter m³','Org. Debris m²','Org. Debris m³']
        area_param = (128*self.gsd*0.01)**2

        arr_data = np.zeros((len(label), 1), dtype='int64')
        arr_data[:,0] = [np.sum(self.c_matrix == i) for i in range(len(label))]

        litter_h = arr_data[label.index('Litter - high')]
        litter_l = arr_data[label.index('Litter - low')]
        org_debris = arr_data[label.index('Organic debris')]

        arr_data[label.index('Litter abundances')] = (litter_h*self.dense_few[0] + litter_l*self.dense_few[1])*self.alt_correct
        arr_data[label.index('Litter m²')] = litter_h*area_param + litter_l*area_param*0.5 # area
        arr_data[label.index('Litter m³')] = litter_h*area_param*0.30 + litter_l*area_param*0.07 # volume
        arr_data[label.index('Org. Debris m²')] = org_debris*area_param # area
        arr_data[label.index('Org. Debris m³')] = org_debris*area_param*0.1 # volume

        self.df = pd.DataFrame(arr_data, columns = ['result'], index = label)

        return self.df

class PLQ_df(results_df):
    def __init__(self, *args):
        super().__init__(*args)

    def get_dataframe(self):
        label, correction_params = self.load_configs()
        arr_data = np.zeros((len(label),2), dtype='int64')

        for i in range(len(label)):
            class_sum = int(np.sum(self.c_matrix==i)*self.alt_correct)
            arr_data[i]  = class_sum, class_sum*correction_params[i]

        self.df = pd.DataFrame(arr_data, columns = ['classifications','assessed abundances'], index = label)

        return self.df
         
     