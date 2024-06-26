import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from WCS.Zone_mng import zone_manager
class wh_manager ():
    def __init__(self, WH_properties):
        self.Zone_dict = {}
        self.WH_NAME = WH_properties['WH_name']
    
    # def __init__(self, **kwargs):
    #     pass
    
    def add_zone(self, 
                 zone_properties_dict
                 ):
        

        zone_name = zone_properties_dict['Zone_name']
        self.Zone_dict[zone_name] = \
            locals()[zone_name] = \
                    zone_manager(
                        zone_properties_dict
                        )
        

        


    def add_default_zone(self, zone_properties_dict):
        # Zone_01 = zone_manager
        # Zone_01.__init__(self, **zone_properties_dict)

        Zone_01 = zone_manager(zone_properties_dict)
        # Zone_01.Area_dict = 
        # Zone_01.add_default_areas(self)
        zone_manager.add_default_areas(Zone_01)

        self.Zone_dict['Zone_01'] = Zone_01

        return self # self.Zone_dict
        
        # super().add_default_areas()
    
        