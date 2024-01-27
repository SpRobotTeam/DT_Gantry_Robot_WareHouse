from Zone_mng import zone_manager
class wh_manager (zone_manager):
    def __init__(self):
        self.Zone_dict = {}
    
    # def __init__(self, **kwargs):
    #     pass
    
    def add_zone(self, 
                 zone_properties_dict, 
                 in_properties_dict = None, 
                 out_properties_dict = None, 
                 device_properties_dict = None, 
                 ):
        


        self.Zone_dict[zone_properties_dict['name']] = \
            globals (
                    f"{zone_properties_dict['name']}", 
                    zone_manager(zone_properties_dict))
        


    def add_default_zone(self, **container):
        self.Zone_01 = zone_manager
        self.Zone_01.__init__(self, **container)
        self.Zone_dict['Zone_01'] = self.Zone_01
        self.Zone_01.Area_dict = self.add_default_areas()

        return self.Zone_dict
        
        # super().add_default_areas()
    
        