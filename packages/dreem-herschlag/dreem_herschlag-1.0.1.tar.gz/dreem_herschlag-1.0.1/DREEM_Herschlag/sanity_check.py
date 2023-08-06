
import pandas as pd
import os
import yaml
from DREEM_Herschlag.util import Path


class Sanity_check(object):
    def __init__(self, config) -> None:
        self.samples = config['samples']
        self.files_per_sample = config['files_per_sample']
        self.path_to_data = config['path_to_data'] if config['path_to_data'][-1] == '/' else config['path_to_data'] + '/'
        self.sample_file = self.path_to_data+'samples.csv'
        self.dreem_args = config['dreem_args']
        self.verbose = config['verbose']
        self.path = Path()

    def files(self):
        # check that every file is there
        for s in self.samples:
            for f in self.files_per_sample:
                assert os.path.exists(self.path_to_data+s+'/'+f), f"{self.path_to_data}{s}/{f} doesn't exist"
        assert os.path.exists(self.sample_file), f"{self.sample_file} doesn't exist"

    def check_samples(self):
        if self.verbose: print(f"Checking {self.sample_file}")
        # check the sanity of samples.csv
        df = pd.read_csv(self.sample_file)
        assert len(df['sample']) == len(df['sample'].unique()), "Every line isn't unique in samples.csv"

        # check that every sample as a corresponding line of samples.csv
        for s in self.samples:
            assert s in list(df['sample']), f"{s} doesn't have a corresponding line in samples.csv"

        with open(self.path.sample_attribute_path, 'r') as f:
            sample_attributes = yaml.safe_load(f)

        assert len(df['exp_env'].unique()) == 1, "exp_env is not unique in samples.csv"
        exp_env = df['exp_env'].unique()[0]

        # check that every column of samples.csv is in sample_attributes.yml
        assert exp_env in ['in_vivo','in_vitro'], f"{exp_env} is not a valid value for exp_env. Should be in_vivo or in_vitro"
        # Check that you have all mandatory columns
        for mand in sample_attributes['mandatory']['all'] + sample_attributes['mandatory'][exp_env]:
            assert mand in list(df.columns), f"{mand} is not in samples.csv"
        
        # Drop unauthorised columns
        for col in list(df.columns):
            if col not in sample_attributes['mandatory']['all'] + sample_attributes['mandatory'][exp_env] \
                + sample_attributes['optional']['all'] + sample_attributes['optional'][exp_env]:
                if col in sample_attributes['optional']: 
                    if self.verbose: print(f"Ignored {col}, not in sample_attributes")
                    df = df.drop(columns=col)

        df.to_csv('temp/samples.csv', index=False)
        if self.verbose: print('Checking samples.csv done\n')
        return 1

    def check_library(self,s):
        # check the sanity of libraries.csv
        if self.verbose: print(f"Checking {s}/library.csv")
        df = pd.read_csv(self.path_to_data+s+'/library.csv')
        assert 'name' in list(df.columns), "name is not in library.csv"
        assert len(df['name']) == len(df['name'].unique()), f"Every name isn't unique in {s}/library.csv"
        with open(self.path.library_attributes_path, 'r') as f:
            library_attributes = yaml.safe_load(f)
        # check that every mandatory column is there
        for mand in library_attributes['mandatory']:
            assert mand in list(df.columns), f"{mand} is not in {s}/library.csv"
        # check that every column of libraries.csv is in resources/library_attributes.yml
        for col in list(df.columns):
            if col not in library_attributes['mandatory'] + library_attributes['optional']:
                if self.verbose: print(f"Ignored {col}, not in library_attributes")
                df = df.drop(columns=col)
        if not os.path.exists(f"temp/{s}"):
            os.mkdir(f"temp/{s}")
        df.to_csv(f"temp/{s}/library.csv", index=False)

        if self.verbose: print(f"Checking {s}/library.csv done\n")

    def run(self):
        if self.verbose: print("Checking files")
        self.files()
        self.check_samples()
        for s in self.samples:
            self.check_library(s)
        if self.verbose: print("Checking files done\n")
        return 1