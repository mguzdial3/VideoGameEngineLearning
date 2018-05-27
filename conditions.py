#The basic idea of a condition
class Condition(object):
	def __init__(self, frameObject):
		self.pastFrames = 0
		self.frameObject = frameObject
		self.isPlayerRule = False

	def UpdatePastFrames(self):
		self.pastFrames +=1

class VelocityXCondition(Condition):
	def __init__(self, frameObject, velocityVal):
		super(VelocityXCondition,self).__init__(frameObject)
		self.spriteName = frameObject.name
		self.velocityValue = velocityVal

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.spriteName==other.spriteName and self.pastFrames==other.pastFrames and self.velocityValue==other.velocityValue
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, self.velocityValue]))

	def clone(self):
		condition = VelocityXCondition(self.frameObject, self.velocityValue)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "VelocityXCondition: "+str([self.spriteName, self.velocityValue])

class VelocityYCondition(Condition):
	def __init__(self, frameObject, velocityVal):
		super(VelocityYCondition,self).__init__(frameObject)
		self.spriteName = frameObject.name
		self.velocityValue = velocityVal

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.spriteName==other.spriteName and self.pastFrames==other.pastFrames and self.velocityValue==other.velocityValue
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, self.velocityValue]))

	def clone(self):
		condition = VelocityYCondition(self.frameObject, self.velocityValue)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "VelocityYCondition: "+str([self.spriteName, self.velocityValue])


#Animation State and not exists
class AnimationCondition(Condition):
	def __init__(self, frameObject, existsSpriteName):
		super(AnimationCondition,self).__init__(frameObject)
		self.spriteName = existsSpriteName
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		if not frameObject==None:
			self.x = frameObject.x
			self.y = frameObject.y
			self.width = frameObject.width
			self.height = frameObject.height

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.spriteName==other.spriteName and self.pastFrames==other.pastFrames and self.x==other.x and self.y==other.y
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, self.x, self.y]))

	def clone(self):
		condition = AnimationCondition(self.frameObject, self.spriteName)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "AnimationCondition: "+str([self.spriteName, self.x, self.y, self.width, self.height])

#screen position of sprites
class SpatialCondition(Condition):
	def __init__(self, frameObject, sprite1, spritePosition):
		super(SpatialCondition,self).__init__(frameObject)
		self.spriteName = sprite1
		self.screenPosition = spritePosition

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.spriteName==other.spriteName and self.screenPosition==other.screenPosition and self.pastFrames==other.pastFrames
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, tuple(self.screenPosition)]))

	def clone(self):
		condition = SpatialCondition(self.frameObject, self.spriteName, self.screenPosition)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "SpatialCondition: "+str([self.spriteName, self.screenPosition])

#relationships between sprites
class RelationshipConditionX(Condition):
	def __init__(self, frameObject, sprite1, sprite2, connect1, connect2, relativeVectorVal):
		super(RelationshipConditionX,self).__init__(frameObject)
		self.spriteName = sprite1
		self.sprite1Edge = connect1
		self.sprite2Name = sprite2
		self.sprite2Edge = connect2
		self.relativeVectorVal = relativeVectorVal

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.sprite2Edge==other.sprite2Edge and self.sprite1Edge==other.sprite1Edge and self.sprite2Name==other.sprite2Name and self.spriteName==other.spriteName and self.pastFrames==other.pastFrames and self.relativeVectorVal == other.relativeVectorVal
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, self.sprite1Edge, self.sprite2Name, self.sprite2Edge, self.relativeVectorVal]))

	def clone(self):
		condition = RelationshipConditionX(self.frameObject, self.spriteName, self.sprite2Name, self.sprite1Edge, self.sprite2Edge, self.relativeVectorVal)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "RelationshipConditionX: "+str([self.spriteName, self.sprite1Edge, self.sprite2Name, self.sprite2Edge, self.relativeVectorVal])

#relationships between sprites
class RelationshipConditionY(Condition):
	def __init__(self, frameObject, sprite1, sprite2, connect1, connect2, relativeVectorVal):
		super(RelationshipConditionY,self).__init__(frameObject)
		self.spriteName = sprite1
		self.sprite1Edge = connect1
		self.sprite2Name = sprite2
		self.sprite2Edge = connect2
		self.relativeVectorVal = relativeVectorVal

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.sprite2Edge==other.sprite2Edge and self.sprite1Edge==other.sprite1Edge and self.sprite2Name==other.sprite2Name and self.spriteName==other.spriteName and self.pastFrames==other.pastFrames and self.relativeVectorVal == other.relativeVectorVal
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.spriteName, self.sprite1Edge, self.sprite2Name, self.sprite2Edge, self.relativeVectorVal]))

	def clone(self):
		condition = RelationshipConditionY(self.frameObject, self.spriteName, self.sprite2Name, self.sprite1Edge, self.sprite2Edge, self.relativeVectorVal)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "RelationshipConditionY: "+str([self.spriteName, self.sprite1Edge, self.sprite2Name, self.sprite2Edge, self.relativeVectorVal])

#Variable relationships
class VariableCondition(Condition):
	def __init__(self, frameObject, variableName, variableValue):
		super(VariableCondition,self).__init__(frameObject)
		self.variableName = variableName
		self.variableValue = variableValue

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.variableValue==other.variableValue and self.variableName==other.variableName and self.pastFrames==other.pastFrames
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.pastFrames, self.variableName, self.variableValue]))

	def clone(self):
		condition = VariableCondition(self.frameObject, self.variableName, self.variableValue)
		condition.pastFrames = self.pastFrames
		condition.isPlayerRule = self.isPlayerRule
		return condition

	def __str__(self):
		return "VariableCondition: "+str([self.variableName, self.variableValue])