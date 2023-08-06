
from DREEM_Herschlag.resources import __file__ as resources_file
from DREEM_Herschlag import __file__ as DREEM_Herschlag_file


class Path(object):
    def __init__(self) -> None:    
        self.resources_file = '/'.join(resources_file.split('/')[:-1])
        self.DREEM_Herschlag_file = '/'.join(DREEM_Herschlag_file.split('/')[:-1])
        self.sample_attribute_path = self.resources_file+'/sample_attributes.yml'
        self.library_attributes_path = self.resources_file+'/library_attributes.yml'

