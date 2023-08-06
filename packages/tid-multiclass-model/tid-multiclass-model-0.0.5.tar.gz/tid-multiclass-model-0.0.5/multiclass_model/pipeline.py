from feature_engine.encoding import OrdinalEncoder
from feature_engine.selection import DropFeatures

from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline

from multiclass_model.config.core import config

from multiclass_model.custom_functions import custom_functions as cf
from processing.data_manager import load_json
from config.core import config

TypeEnt_number_maps = load_json(file_name=config.app_config.json_file_TypeEnt)

category_prediction_pipeline = Pipeline([

    ('splitter',
     cf.splitter(variables = config.model_config.split_features, 
        new_variable_names = config.model_config.split_features_names)
    ),


    ('GCL_Code-cardinal-ordering',
     OrdinalEncoder(encoding_method='ordered', variables = config.model_config.ordinal_encode)
    ),
    
    ('TypeEnt_number_map_modes', 
    cf.Mapper(variables = config.model_config.mapper_encode, mappings = TypeEnt_number_maps)
    ),
    
    ('drop_features',
     DropFeatures(features_to_drop= config.model_config.drop_features)
    ),
    
    ('Fill_na',
    cf.Custom_Fillna(variables = config.model_config.fillna_features, fill_value = 0)
    ),
    
    ('KNN', OneVsRestClassifier(KNeighborsClassifier(n_neighbors = config.model_config.n_neighbors)))
    
])
