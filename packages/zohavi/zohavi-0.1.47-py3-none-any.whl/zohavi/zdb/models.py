import json, datetime 

from sqlalchemy import DateTime, Column



############################################################################################################
############################################################################################################
class TBL_Default(object  ):
	sys_created_on = Column( DateTime,  default=datetime.datetime.utcnow ) 
	sys_changed_on = Column( DateTime ) 
	def __getitem__(self, field):
		return self.__dict__.get( field )

	def keys(self):
		return self.__dict__.keys()

	def to_str(self):
		printStr = ""
		for key in self.keys():
			if '_sa_instance_state' in key: continue	#skip internal variable
			printStr = printStr + str(key) + ":[" +  str( self.__dict__[ key ]) + "], "
		return "<<" + self.__class__.__name__ + ">> # " +  printStr
 
	def to_dict(self):
		dict_obj = {}
		for c in self.__table__.columns:
			value = getattr(self, c.name)
			dict_obj[c.name] = value.isoformat() if isinstance(value, datetime.datetime) else value
		return dict_obj

	def to_json(self):
		return json.dumps( self.to_dict() )
 