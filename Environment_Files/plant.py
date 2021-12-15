
class Plant:
	def __init__(self, plant_dict, x_loc, y_loc):
		self.name = plant_dict["Name"]
		self.x_loc = x_loc
		self.y_loc = y_loc
		self.harvest_age = plant_dict["Harvest_Age"]
		self.space_requirement = plant_dict["Space_Requirement"]
		self.incident_light = 0
		self.stage_name = plant_dict["Filenames"][0]
		self.light_requirement = plant_dict["Light_Requirement"]

	def plant_grow(self):
		print("Incident Light:",self.incident_light)
		# pass

