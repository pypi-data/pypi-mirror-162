import os
from importlib import import_module
from datetime import datetime

class EntryPoint:
    def __init__(self, entry_point, from_source_repo=False):
        self.entry_name = entry_point[:-3].replace(os.sep, '.') # *.*.*.py > *.*.*
        self.source = import_module(self.entry_name)

        if not from_source_repo:
            self.mlops_entry_point = datetime.today().strftime(saving_time_format) + '-' + entry_point
        else:
            self.mlops_entry_point = os.path.split(entry_point)[1]
        
        # Structured Functions
        assert hasattr(self.source, 'preprocessing') 
        assert hasattr(self.source, 'architecture') 
        assert hasattr(self.source, 'train') 
        self.preprocessing = getattr(self.source, 'preprocessing')  # return datasets
        self.architecture = getattr(self.source, 'architecture')    # return user_models
        self.train = getattr(self.source, 'train')                  # return model

        # Unstructured Functions
        if hasattr(self.source, 'predict'):
            self.predict = getattr(self.source, 'predict')
        if hasattr(self.source, 'evaluate'):
            self.evaluate = getattr(self.source, 'evaluate')            # return metrics
        if hasattr(self.source, 'report'):
            self.report = getattr(self.source, 'report')                # return report


