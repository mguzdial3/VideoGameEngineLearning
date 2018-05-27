import csv, shutil, sys, os, copy, glob, pickle
sys.path.append('/usr/local/lib/python2.7/site-packages')
import random, math
import numpy as np
from Queue import PriorityQueue

#Hogwarts42! wordpress
playerAccelerations = ["./Megaman-longplay5/playerAccelerationTrack.csv"]
spriteAccelerations = ["./Megaman-longplay5/spriteAccelerationTrack.csv"]
spritesListings = ["./Megaman-longplay5/spriteDescripts.csv"]
cameraPositions = ["./camera5Positions-Bombman.csv"]
startAndEndFrames =[[33418, 38847]]#220 (Video 4) 338 is precoin make
#33368, 38314
#37280 is end of pre-boss section
#34868 is one minute in 
#Video 5: 395-1939 
#4: 220-1789
#663 is 1/3 of train level
#845 is 1/3 through the level


#33489
#33559

class EngineNode:
	def __init__(self, myParent, engine, distanceToGoal=0):
		#self.parent = myParent
		self.engine = engine
		self.distanceFromRoot = 0
		self.distanceToGoal = distanceToGoal
		if not myParent ==None:
			self.distanceFromRoot = myParent.distanceFromRoot+1

	def GetTotalDistance(self):
		return self.distanceFromRoot+self.distanceToGoal

#simulated annealing/GA algorithm
#montecarlo

#A single engine. transforms rules (in the form of Conditions)
class Engine:
	def __init__(self, parent):
		self.rules = []
		self.controlRules = []
		self.totalRules = []
		self.parentEngine = None
		if not parent == None:
			self.rules = list(parent.rules)
			self.controlRules = list(parent.controlRules)
			self.totalRules = list(self.rules+self.controlRules)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			if len(self.rules)==len(other.rules) and len(self.controlRules)==len(other.controlRules):
				for index in range(0, len(self.rules)):
					if not self.rules[index]==other.rules[index]:
						return False
				for index in range(0, len(self.controlRules)):
					if not self.controlRules[index]==other.controlRules[index]:
						return False
				return True
			else:
				return False
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple(self.rules), tuple(self.controlRules), tuple(self.totalRules))

	def RemoveRule(self, rule):
		if rule in self.rules:
			self.rules.remove(rule)

		if rule in self.controlRules:
			self.controlRules.remove(rule)

		if rule in self.totalRules:
			self.totalRules.remove(rule)

	def ReplaceRule(self, oldRule, newRule, oldEngine):

		if oldRule in oldEngine.rules:
			ruleIndex = oldEngine.rules.index(oldRule)
			if not ruleIndex == -1 and ruleIndex<len(self.rules):
				self.rules[ruleIndex] = newRule

		if oldRule in oldEngine.controlRules:
			ruleIndex = oldEngine.controlRules.index(oldRule)
			if not ruleIndex == -1 and ruleIndex<len(self.controlRules):
				self.controlRules[ruleIndex] = newRule

		ruleIndex = oldEngine.totalRules.index(oldRule)
		if not ruleIndex == -1 and ruleIndex<len(self.totalRules ):
			self.totalRules[ruleIndex] = newRule


	def AddRule(self, newRule, prevFrame, goalFrame):

		self.rules.append(newRule)
		self.totalRules.append(newRule)

		if isinstance(newRule.change[0], VelocityXCondition) or isinstance(newRule.change[0], VelocityYCondition):
			rulesToUpdate = []

			for rule in self.totalRules:
				if rule.activated:
					rulesToUpdate.append(rule)



			frames = PhysicsPredict(prevFrame, self, goalFrame)

			minFrame = None
			minDist = float("inf")

			for frame in frames:
				frameDist = FrameDistance(frame, changeFrames[currIndex])

				if frameDist<minDist:
					minDist = frameDist
					minFrame = frame


			minConditions = minFrame.ReallyGetConditions()
			minConditionsSet = set(minConditions)


			framesPlus = Predict(prevFrame, self, goalFrame)

			minFramePlus = None
			minDistPlus = float("inf")

			for frame in framesPlus:
				frameDist = FrameDistance(frame, changeFrames[currIndex])

				if frameDist<minDistPlus:
					minDistPlus = frameDist
					minFramePlus = frame


			minConditionsPlus = minFramePlus.ReallyGetConditions()
			minConditionsSetPlus = set(minConditionsPlus)

			for rule in rulesToUpdate:
				rule.activated = True
				if isinstance(rule.change[0], VelocityXCondition) or isinstance(rule.change[0], VelocityYCondition):
					#if this rule was activated last frame, make sure adding new rule won't break that
					for precog in rule.preconditions:
						precog.conditionList = list(minConditionsSet.intersection(precog.conditionList))
						precog.changeConditions = list(minConditionsSet.intersection(precog.changeConditions))
				else:
					#if this rule was activated last frame, make sure adding this rule won't break that
					for precog in rule.preconditions:
						precog.conditionList = list(minConditionsSetPlus.intersection(precog.conditionList))
						precog.changeConditions = list(minConditionsSetPlus.intersection(precog.changeConditions))
					

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

class RulePrecondition:
	def __init__(self, initialConditionList, changeFrameObj):
		self.conditionList = list(initialConditionList)
		self.changeConditions = []
		self.frameObject = changeFrameObj
		if not self.frameObject == None:
			for condition in self.conditionList:
				if self.frameObject==condition.frameObject:
					self.changeConditions.append(condition)

	def clone(self):
		newConditionList = []
		for condition in self.conditionList:
			newConditionList.append(condition.clone())

		cloned = RulePrecondition(newConditionList, self.frameObject)

		for condition in self.changeConditions:
			cloned.changeConditions.append(condition.clone())

		return cloned

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.conditionList == other.conditionList and self.changeConditions==other.changeConditions
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([hash(tuple(conditionList)), hash(tuple(self.changeConditions))]))

class Rule:
	def __init__(self, initialPreconditions, changePair):
		self.preconditions = initialPreconditions
		self.change = changePair#pair of conditions that constitutes this rule, rest of conditions are explanation
		self.framesUsed = []
		self.activated = False

	def clone(self):
		preconditionCopy = []
		for precog in self.preconditions:
			preconditionCopy.append(precog.clone())

		changePair = [self.change[0].clone(), self.change[1].clone()]
		cloned =Rule(preconditionCopy, changePair)
		cloned.framesUsed = self.framesUsed
		cloned.activated = self.activated
		return cloned

	def isTriggered(self, conditions, printIt=False):

		if printIt:
			print "   isTriggered Rule: "+str(self.change[0])+"->"+str(self.change[1])
		
		for precog in self.preconditions:
			activeVal = len(precog.conditionList)

			for condition in precog.conditionList:
				if condition in conditions:
					#if printIt:
					#	print "   isTriggered Condition match: "+str(condition)
					activeVal-=1
				else:
					if printIt:
						print "   isTriggered Condition not-match: "+str(condition)
					break
			if activeVal==0:#Has all the right conditions, has to check if it matches
				return precog

		return None

	def __str__(self):
		return "Rule: "+str(self.change[0])+"->"+str(self.change[1])+"<"+str(self.activated)+">"

	def Activate(self, precog, frame):

		self.activated = True
		#print "Hit Activate Rule: "+str(self)+" with precog change conditions: "+str(len(precog.changeConditions))
		if not self.framesUsed:
			self.framesUsed.append(frame.number)

		newFrame = frame.clone()
		#print "HIT ACTIVATE"
		#How to activate based on conditions
		frameObjectToChange = None

		#print "  Hit the else"
		#print "  Instance of Animation Condition: "+str(isinstance(self,AnimationCondition))
		#print "  Change 0 to 1: "+str([self.change[0].frameObject, self.change[1].frameObject])
		if len(precog.changeConditions)==0 and self.change[0].frameObject==None and self.change[1].frameObject==None:
			#Condition Change
			if "cameraPosX" in self.change[0].variableName:
				newFrame.cameraX += self.change[1].variableValue-self.change[0].variableValue
			elif "cameraPosY" in self.change[0].variableName:
				newFrame.cameraY += self.change[1].variableValue-self.change[0].variableValue
			else:
				variableName = variableName[:-1*len("change")]#TODO; will this ever happen? Except for camera?
				for condition in newFrame.conditions:
					if isinstance(condition, VariableCondition):
						if condition.name == variableName:
							condition.variableValue += change[1].variableValue-change[0].variableValue
			return newFrame
		elif isinstance(self.change[0],AnimationCondition) and self.change[0].frameObject==None and self.change[1].frameObject!=None:
			#Instantiate
			#print "Instantiate: "+self.change[1].frameObject.name
			newFrame.frameObjects.append(FrameObject(self.change[1].frameObject.name, self.change[1].frameObject.x, self.change[1].frameObject.y, self.change[1].frameObject.width, self.change[1].frameObject.height, 1.0, 0, 0))
			return newFrame
		else:
			#Find frameObject based on precog
			frameObjectsToChange = []
			nameToMatch = self.change[0].frameObject.name
			#print "Rule "+str(self)+" toMatch num: "+str(len(precog.changeConditions))
			for frameObj in newFrame.frameObjects:
				if frameObj.name==nameToMatch:
					objConditions = frameObj.GetConditions(newFrame)
					toMatch = len(precog.changeConditions)

					for condition in precog.changeConditions:
						if condition in objConditions:
							toMatch-=1

					if toMatch==0:
						frameObjectsToChange.append(frameObj)

			if self.change[0].isPlayerRule and not frame.player in frameObjectsToChange:
				frameObjectsToChange.append(frame.player)

			while None in frameObjectsToChange:
				frameObjectsToChange.remove(None)

			for frameObj in frameObjectsToChange:
				#print "Rule "+str(self)+" activated on: "+str(frameObj)

				#Changed so that this happens for each correct frameobject
				#frameIndex = frame.frameObjects.index(frameObj)
				#if frameIndex<len(newFrame.frameObjects):
				#frameObjectToChange = newFrame.frameObjects[]
				frameObjectToChange = frameObj

				#Walk through all of the possible conditions for frameObjects and implement
				if isinstance(self.change[0],AnimationCondition):
					if self.change[1].spriteName=="None":
						if frameObjectToChange in newFrame.frameObjects:
							newFrame.frameObjects.remove(frameObjectToChange)
					else:
						frameObjectToChange.name =	self.change[1].spriteName
						frameObjectToChange.width = self.change[1].width
						frameObjectToChange.height = self.change[1].height
				elif isinstance(self.change[1], VelocityYCondition):
					frameObjectToChange.velocity = [frameObjectToChange.velocity[0], self.change[1].velocityValue]
				elif isinstance(self.change[1], VelocityXCondition):
					frameObjectToChange.velocity = [self.change[1].velocityValue, frameObjectToChange.velocity[1]]
				elif isinstance(self.change[0], SpatialCondition):
					frameObjectToChange.x = self.change[1].screenPosition[0]
					frameObjectToChange.x = self.change[1].screenPosition[1]
				elif isinstance(self.change[0], RelationshipConditionX) or isinstance(self.change[0], RelationshipConditionY):
					secondFrameObject = None
					for frameObj in newFrame.frameObjects:
						if frameObj.name == self.change[0].sprite2Name:
							#check that the distance between the frameObj and secondFrameObj matches change[0]
							minCondition = GetMinConnectionBetweenTwoSprites(frameObjectToChange, frameObj)
							if minCondition== self.change[0]:
								secondFrameObject = frameObj
							break

					if isinstance(self.change[0], RelationshipConditionX):
						sprite1Edge = self.change[1].sprite1Edge
						pointGotten = GetPoint(sprite1Edge, frameObjectToChange)
						if pointGotten==None:
							pointGotten = [0,0]
						startX = (frameObjectToChange.x-pointGotten[0])
						endX = self.change[0].relativeVectorVal*4
						pointB = GetPoint(self.change[1].sprite2Edge, secondFrameObject)
						if pointB==None:
							pointB = [0,0]
						frameObjectToChange.x = startX+ pointB[0]+endX

					else:
						pointGotten = GetPoint(self.change[1].sprite1Edge, frameObjectToChange)
						if pointGotten==None:
							pointGotten = [0,0]
						pointB = GetPoint(self.change[1].sprite2Edge, secondFrameObject)
						if pointB==None:
							pointB = [0,0]
						frameObjectToChange.y = (frameObjectToChange.y-pointGotten[1])+ pointB[1]+self.change[1].relativeVectorVal*4
						
									
		#Variable conditions can't be change conditions except for Camera (which is already handled above)
		return newFrame

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.change[0]== other.change[0] and self.change[1] == other.change[1] and self.preconditions==other.preconditions
		else:
			return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([hash(self.change[0]), hash(self.change[1]), hash(tuple(self.preconditions))]))

def GetLine(lineName, frameObj):
	if lineName=="North":
		return frameObj.GetNorthLine()
	elif lineName=="South":
		return frameObj.GetSouthLine()
	elif lineName=="East":
		return frameObj.GetEastLine()
	elif lineName=="West":
		return frameObj.GetWestLine()

def GetPoint(lineName, frameObj):
	if frameObj==None:
		return [0,0]

	if lineName=="North":
		return frameObj.GetNorthPoint()
	elif lineName=="South":
		return frameObj.GetSouthPoint()
	elif lineName=="East":
		return frameObj.GetEastPoint()
	elif lineName=="West":
		return frameObj.GetWestPoint()


def spriteTranslate(spriteName):
	backgroundSignifiers = ["S", "W", "B", "L", "R"]

	#Remove all background signifiers
	if spriteName[len(spriteName)-1] in backgroundSignifiers:
		spriteName = spriteName[:len(spriteName)-1]

	#TODO; remove this after animation stuff
	numberSignifiers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
	for number in numberSignifiers:
		if number in spriteName:
			spriteName = spriteName[:spriteName.index(number)]

	return spriteName

def CheckHorizontalSides(side1, side2):
	parallelMatches = [["North", "North"], ["North", "South"], ["South", "South"]]

	for pairMatch in parallelMatches:
		if (side1==pairMatch[0] and side2==pairMatch[1]) or (side1==pairMatch[1] and side2==pairMatch[0]):
			return True

	return False

def CheckVerticalSides(side1, side2):
	parallelMatches = [["East", "East"], ["East", "West"], ["West", "West"]]
	for pairMatch in parallelMatches:
		if (side1==pairMatch[0] and side2==pairMatch[1]) or (side1==pairMatch[1] and side2==pairMatch[0]):
			return True
	return False

def parallelLineDistance(point1, point2, line1, line2):
	uTop = (point2[0]-line1[0][0])*(line1[1][0]-line1[0][0])+(point2[1]-line1[0][1])*(line1[1][1]-line1[0][1])
	vMag = math.pow(line1[1][0]-line1[0][0], 2)+math.pow(line1[1][1]-line1[0][1], 2)
	u=0
	if vMag>0:
		u = uTop/vMag
	x = line1[0][0]+ u*(line1[1][0]-line1[0][0])
	y = line1[0][1]+u*(line1[1][1]-line1[0][1])
	diffVector = [x-point2[0], y-point2[1]]
	diffMag = math.sqrt(math.pow(diffVector[0], 2)+math.pow(diffVector[1], 2))
	return diffMag

def dotProduct(line1, line2):
	return line1[0]*line2[0]+line1[1]*line2[1]

def pointDistance(point1, point2):
	return math.sqrt(math.pow(point1[0]-point2[0], 2)+math.pow(point1[1]-point2[1], 2))

def GetMinConnectionBetweenTwoSprites(sprite1, sprite2):
	sides1 = ["North", "North", "South", "South", "East", "East", "West", "West", "Center"]
	sides2 = ["North", "South", "South", "North", "East", "West", "West", "East", "Center"]

	minConnection = None
	minDist = float("inf")
	minVector = [0,0]
	for i in range(len(sides1)):
		thisDist = float("inf")
		thisVector = [0,0]
		if i<len(sides1)-1:
			p1 = GetPoint(sides1[i], sprite1)
			p2 = GetPoint(sides2[i], sprite2)
			v1 = GetLine(sides1[i], sprite1)
			v2 = GetLine(sides2[i], sprite2)
			thisDist = parallelLineDistance(p1, p2, v1, v2)
			thisVector = [p1[0]-p2[0], p1[1]-p2[1]]
		else:
			p1 = (sprite1.x, sprite1.y)
			p2 = (sprite2.x, sprite2.y)
			thisDist = pointDistance(p1, p2)
			thisVector = [p1[0]-p2[0], p1[1]-p2[1]]

		intDivision = int(4)
		thisDist = int(thisDist/intDivision)
		thisVector[0] = int(thisVector[0]/intDivision)
		thisVector[1] = int(thisVector[1]/intDivision)
		if thisDist<minDist:
			minVector = thisVector
			minDist = thisDist
			minConnection = [sprite1, sprite1.name, sprite2.name, sides1[i], sides2[i], minVector]

	return minConnection

class FrameObject:
	def __init__(self, name, positionX, positionY, width, height, confidence, velocityX, velocityY):
		self.name = name
		self.x = positionX #middle of sprite
		self.y =  positionY #middle of sprite
		self.width = width
		self.height = height
		self.confidence = confidence
		self.velocity = (velocityX,velocityY)

	def clone(self):
		newFrameObj = FrameObject(self.name, self.x, self.y, self.width, self.height, self.confidence, self.velocity[0], self.velocity[1])
		return newFrameObj

	#Get a list of the four cordinal points
	def GetPoints(self):
		pts = []
		pts.append(self.GetWestPoint())#left
		pts.append(self.GetEastPoint())#right
		pts.append(self.GetNorthPoint())#top
		pts.append(self.GetSouthPoint())#bottom
		return pts

	def GetNorthPoint(self):
		return [self.x,self.y-self.height/2.0]
	def GetSouthPoint(self):
		return [self.x,self.y+self.height/2.0]
	def GetEastPoint(self):
		return [self.x+self.width/2.0,self.y]
	def GetWestPoint(self):
		return [self.x-self.width/2.0,self.y]

	def GetNorthLine(self):
		return [ (self.x-self.width/2.0, self.y-self.height/2.0), (self.x+self.width/2.0, self.y-self.height/2.0)]
	def GetSouthLine(self):
		return [ (self.x-self.width/2.0, self.y+self.height/2.0), (self.x+self.width/2.0, self.y+self.height/2.0)]
	def GetEastLine(self):
		return [ (self.x+self.width/2.0, self.y-self.height/2.0), (self.x+self.width/2.0, self.y+self.height/2.0)]
	def GetWestLine(self):
		return [ (self.x-self.width/2.0, self.y-self.height/2.0), (self.x-self.width/2.0, self.y+self.height/2.0)]

	def __eq__(self, other):
		if isinstance(other, FrameObject):
			return self.name==other.name and self.x==other.x and self.y==other.y
		return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(tuple([self.name, self.x, self.y]))

	def __str__(self):
		return "FrameObject: "+str([self.name, self.x, self.y, self.width, self.height, self.velocity])

	def GetConditions(self, frame):
		conditions = []
		conditions.append(AnimationCondition(self, self.name))
		conditions.append(VelocityXCondition(self, self.velocity[0]))
		conditions.append(VelocityYCondition(self, self.velocity[1]))
		conditions.append(SpatialCondition(self, self.name, [self.x, self.y]))
		for frameObj in frame.frameObjects:
			if not frameObj==self:
				minCondition = GetMinConnectionBetweenTwoSprites(self, frameObj)
				minConditionX = RelationshipConditionX(minCondition[0], minCondition[1], minCondition[2], minCondition[3], minCondition[4], minCondition[5][0])
				conditions.append(minConditionX)
				minConditionY = RelationshipConditionY(minCondition[0], minCondition[1], minCondition[2], minCondition[3], minCondition[4], minCondition[5][1])
				conditions.append(minConditionY)

		return conditions

class Change:
	def __init__(self, spriteName, prevCondition, postCondition):
		self.spriteName = spriteName
		self.prevCondition = prevCondition
		self.postCondition = postCondition

class Frame: 
	def __init__(self, number):
		self.cameraX = 0
		self.cameraY = 0
		self.number = number
		self.frameObjects = []#List of FrameObject objects
		self.spritesContained = []#List of string values for frameobjects that exist in this frame
		self.frameScreen = {}
		self.player = None
		self.conditions = []

	def ReallyGetConditions(self):
		if len(self.conditions)==0:
			self.GetFrameConditions()

		return self.conditions

	def __eq__(self, other):
		if isinstance(other, FrameObject):
			return self.cameraX==other.cameraX and self.cameraY==other.cameraY and tuple(self.ReallyGetConditions())==tuple(other.ReallyGetConditions())
		return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(self.cameraX, self.cameraY, tuple(self.ReallyGetConditions()))	

	def SetCameraX(self, camX, prevX):
		self.cameraX = camX
		cameraMovement = camX-prevX
		if cameraMovement>0:
			for obj in self.frameObjects:
				if not obj.velocity[0]==0:
					obj.velocity = [obj.velocity[0]+cameraMovement, obj.velocity[1]]

	def SetCameraY(self, camY, prevY):
		self.cameraY = camY
		cameraMovement = camY-prevY
		if cameraMovement>0:
			for obj in self.frameObjects:
				if not obj.velocity[1]==0:
					obj.velocity = [obj.velocity[0], obj.velocity[1]+cameraMovement]

	def clone(self):
		cloneFrame = Frame(self.number)
		cloneFrame.cameraX = self.cameraX
		cloneFrame.cameraY = self.cameraY
		for frameObj in self.frameObjects:
			newFrameObj = frameObj.clone()
			cloneFrame.frameObjects.append(newFrameObj)
			if not newFrameObj.name in cloneFrame.spritesContained:
				cloneFrame.spritesContained.append(newFrameObj.name)

			if frameObj==self.player:
				cloneFrame.player = newFrameObj
		cloneFrame.conditions = []
		return cloneFrame

	def AddRow(self, row, isPlayer = False):
		spriteName = spriteTranslate(row[2])
		if spriteName=="None":
			spriteName = spriteTranslate(row[1])

		if isPlayer and not spriteName=="None":
			spriteName = "megaman"

		if len(row)<=7:
			spriteName = spriteTranslate(row[1][:-4])

		if not spriteName=="None":
			if not spriteName in self.spritesContained:
				self.spritesContained.append(spriteName)

			frameObjectToAdd = None
			if len(row)>7:
				if isPlayer:
					frameObjectToAdd=FrameObject(spriteName, float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[11]), float(row[7]), float(row[8]) )
				else:
					#frameObjectToAdd=FrameObject(spriteName, float(row[3]), float(row[4]), float(row[6]), float(row[5]), float(row[11]), float(row[7]), float(row[8]) )
					frameObjectToAdd=FrameObject(spriteName, float(row[3])-float(row[5])/2.0+float(row[6])/2.0, float(row[4])-float(row[6])/2.0+float(row[5])/2.0, float(row[6]), float(row[5]), float(row[11]), float(row[7]), float(row[8]) )
			else:#Added allowance for static frames
				frameObjectToAdd=FrameObject(spriteName, float(row[2])+float(row[4])/2, float(row[3])+float(row[5])/2, float(row[4]), float(row[5]), float(row[6]), 0, 0)

			if not frameObjectToAdd  in self.frameObjects:
				addIt = True
				for inThereObj in self.frameObjects:
					if inThereObj.name==frameObjectToAdd.name and (abs(inThereObj.x-frameObjectToAdd.x)<=4 or abs(inThereObj.y-frameObjectToAdd.y)<=4):
						addIt = False
						break

				if addIt:
					self.frameObjects.append(frameObjectToAdd)
					if isPlayer:
						self.player = frameObjectToAdd

	#calculates and returns self.conditions
	def GetFrameConditions(self):
		self.conditions = []

		for frameObj in self.frameObjects:
			if frameObj!=self.player:
				for condition in frameObj.GetConditions(self):
					self.conditions.append(condition)
		#Player
		if not self.player==None:
			for condition in self.player.GetConditions(self):
				condition.isPlayerRule = True
				self.conditions.append(condition)

		self.conditions.append(VariableCondition(None, "cameraPosX", self.cameraX))
		self.conditions.append(VariableCondition(None, "cameraPosY", self.cameraY))
		return self.conditions

#Determine if string is number
def IsNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def GetPointDistance(pnt1, pnt2):
	xDiff = pnt1[0]-pnt2[0]
	yDiff = pnt1[1]-pnt2[1]
	return (abs(yDiff)+abs(xDiff))

def GetSpriteDistance(sprite1, sprite2):
	spritePoints1 = sprite1.GetPoints()
	spritePoints2 = sprite2.GetPoints()

	minVal = float("inf")

	for pnt1 in spritePoints1:
		for pnt2 in spritePoints2:
			thisVal = GetPointDistance(pnt1, pnt2)
			if thisVal<minVal:
				minVal = thisVal

	return minVal

def FindMinimumSprite(sprite, spriteList):
	minSprite = None
	minDist = float("inf")
	for sprite2 in spriteList:
		if not sprite.name in sprite2.name:
			spriteDist = GetSpriteDistance(sprite, sprite2)
			if spriteDist<minDist:
				minDist = spriteDist
				minSprite = sprite2

	return minSprite

def LinearDistance(x1, y1, x2, y2):
	return abs(x1-x2)+abs(y1-y2)#math.sqrt(pow(x1-x2, 2) + pow(y1-y2, 2))

def CloseEnough(oneSprite, changeSprite, multiplier = 1.5):
	return LinearDistance(oneSprite.x, oneSprite.y, changeSprite.x, changeSprite.y) <(max(oneSprite.width,oneSprite.height)*multiplier+max(changeSprite.width,changeSprite.height)*multiplier)

#Calcultes distance between frames (Hellman's metric)
def FrameDistance(frame1, frame2, doPrint =False):
	if len(frame1.frameScreen.keys())==0:
		frame1.frameScreen = CreateFrameDict(frame1.frameObjects, frame1.player)
	if len(frame2.frameScreen.keys())==0:
		frame2.frameScreen = CreateFrameDict(frame2.frameObjects, frame2.player)

	sumDiff = 0

	for x in range(0,256):
		for y in range(0,224):
			if frame1.frameScreen[x][y]!=frame2.frameScreen[x][y]:
				if doPrint:
					print "   Frame Difference ("+str([x,y])+"): "+str([frame1.frameScreen[x][y], frame2.frameScreen[x][y]])
				sumDiff+=1

	return sumDiff

def CreateFrameDict(frameObjects, player):
	frameScreen = {}

	for x in range(0,256):
		frameScreen[x] = {}
		for y in range(0, 224):
			frameScreen[x][y] =""

	for frameObj in frameObjects:
		if not frameObj.name == "None":
			for x in range(int(frameObj.GetWestPoint()[0]), int(frameObj.GetEastPoint()[0])):
				for y in range(int(frameObj.GetNorthPoint()[1]), int(frameObj.GetSouthPoint()[1])):
					if x<256 and y<224 and x>=0 and y>=0:
						frameScreen[x][y] = frameObj.name
	'''
	if not player==None:
		for x in range(int(player.GetWestPoint()[0]), int(player.GetEastPoint()[0])):
			for y in range(int(player.GetNorthPoint()[1]), int(player.GetSouthPoint()[1])):
				if x<16*26 and y<14*26 and x>=0 and y>=0:
					frameScreen[x][y] = player.name
	'''
	return frameScreen

#Physics prep
def PhysicsPredict(frame, engine, currFrame):
	newFrame = frame.clone()
	
	for rule in engine.rules:
		if isinstance(rule.change[1], VelocityXCondition):
			precog = None#rule.isTriggered(newFrame.ReallyGetConditions())
			
			precog=rule.isTriggered(newFrame.ReallyGetConditions())
			if not precog == None:
				newFrame = rule.Activate(precog, newFrame)
		elif isinstance(rule.change[1], VelocityYCondition):
			precog = rule.isTriggered(newFrame.ReallyGetConditions())
			if not precog == None:
				newFrame = rule.Activate(precog, newFrame)

	frameSet = [newFrame]
	for playerRule in engine.controlRules:
		if isinstance(playerRule.change[1], VelocityXCondition):
			precog=None
			if playerRule.change[1].velocityValue==3.0 and playerRule.change[0].velocityValue==2.0:

				precog=playerRule.isTriggered(newFrame.ReallyGetConditions())
			else:
				precog=playerRule.isTriggered(newFrame.ReallyGetConditions())
			if not precog == None:				
				frameSet.append(playerRule.Activate(precog, newFrame))
		elif isinstance(playerRule.change[1], VelocityYCondition):
			precog=playerRule.isTriggered(newFrame.ReallyGetConditions())
			if not precog == None:				
				frameSet.append(playerRule.Activate(precog, newFrame))
	return frameSet

def RunRules(frameSet, engine, currFrame):
	#Velocity Rule
	currSize = len(frameSet)
	for i in range(currSize):
		for frameObj in frameSet[i].frameObjects:
			frameObj.x += frameObj.velocity[0]
			frameObj.y += frameObj.velocity[1]



	for i in range(currSize):		
		#Camera Rule (Every Engine has this baked in)

		#X POSITION
		cameraChange = currFrame.cameraX-frameSet[i].cameraX
		if not cameraChange==0:
			for frameObj in frameSet[i].frameObjects:
				frameObj.x -=cameraChange

			#Right side check
			for currFrameObj in currFrame.frameObjects:
				if not currFrameObj in frameSet[i].frameObjects:
					if currFrameObj.GetEastPoint()[0]>412-cameraChange-4:
						if not currFrameObj in frameSet[i].frameObjects:
							frameSet[i].frameObjects.append(currFrameObj)
							if not currFrameObj.name in frameSet[i].spritesContained:
								frameSet[i].spritesContained.append(currFrameObj.name)

			#Left side removal check
			toRemove = []
			removedSomething = False
			for frameObj in frameSet[i].frameObjects:
				if frameObj.GetWestPoint()[0]<0:
					toRemove.append(frameObj)
					removedSomething = True

			for removeObj in toRemove:
				frameSet[i].frameObjects.remove(removeObj)

			frameSet[i].spritesContained = []
			for frameObj in frameSet[i].frameObjects:
				if not frameObj.name in frameSet[i].spritesContained:
					frameSet[i].spritesContained.append(frameObj.name)

			frameSet[i].conditions = []
			frameSet[i].frameScreen = {}

		#Y POSITION
		cameraChange = currFrame.cameraY-frameSet[i].cameraY
		if not cameraChange==0:
			for frameObj in frameSet[i].frameObjects:
				frameObj.y -=cameraChange

			#Addition Check
			for currFrameObj in currFrame.frameObjects:
				if not currFrameObj in frameSet[i].frameObjects:
					if currFrameObj.GetNorthPoint()[0]<256+cameraChange or currFrameObj.GetSouthPoint()[0]>cameraChange:
						if not currFrameObj in frameSet[i].frameObjects:
							frameSet[i].frameObjects.append(currFrameObj)
							if not currFrameObj.name in frameSet[i].spritesContained:
								frameSet[i].spritesContained.append(currFrameObj.name)

			#Removal
			toRemove = []
			removedSomething = False
			for frameObj in frameSet[i].frameObjects:
				if frameObj.GetSouthPoint()[0]<0 or frameObj.GetNorthPoint()[0]>244:
					toRemove.append(frameObj)
					removedSomething = True

			for removeObj in toRemove:
				frameSet[i].frameObjects.remove(removeObj)

			frameSet[i].spritesContained = []
			for frameObj in frameSet[i].frameObjects:
				if not frameObj.name in frameSet[i].spritesContained:
					frameSet[i].spritesContained.append(frameObj.name)

			frameSet[i].conditions = []
			frameSet[i].frameScreen = {}
		
		#Learned Rules
		for rule in engine.rules:
			if not isinstance(rule.change[1], VelocityXCondition) and not isinstance(rule.change[1], VelocityYCondition):
				precog = rule.isTriggered(frameSet[i].ReallyGetConditions())
				if not precog ==None:
					#activeRules.append([precog, rule])
					frameSet[i] = rule.Activate(precog,frameSet[i])


		#player can always do nothing (assumed)
		for playerRule in engine.controlRules:
			if not isinstance(playerRule.change[1], VelocityXCondition) and not isinstance(playerRule.change[1], VelocityYCondition):
				precog = playerRule.isTriggered(frameSet[i].ReallyGetConditions())
				if not precog==None:
					frameSet.append(playerRule.Activate(precog, frameSet[i]))
		
	
	return frameSet#set of potential frames (if no rules, returns same frame)


#For each frame, pass in engine and 
def Predict(frame,engine, currFrame):
	for rule in engine.totalRules:
		rule.activated = False 


	frameSet = PhysicsPredict(frame,engine,currFrame)
	return RunRules(frameSet, engine, currFrame)


	

#Sprite to count data
playerRules = []
#superFallio = Rule(Change("supMario", "+Y", "-Y"))
supMarioSpriteName = "ario"
allFramesInfo = {}



for indexOfThings in range(len(playerAccelerations)):
	playerAccelerationCSV =playerAccelerations[indexOfThings]
	spriteAccelerationCSV = spriteAccelerations[indexOfThings]
	spritesCSV = spritesListings[indexOfThings]#"./AdamLevels-Processed/GameplayVideo4Source/AllFrameDescriptions/frameDescriptions1-1.csv"#"./frames5-25fpers/frameDescriptionColorAll.csv"

	#List of stuff in each frame
	changeFrames = {}
	

	#Player Changes
	print ("Player changes")
	source = open(playerAccelerationCSV,"rb")
	reader = csv.reader(source)

	readIt = False

	minFrameIndex = startAndEndFrames[indexOfThings][0]#start of level 1-1
	maxFrame = startAndEndFrames[indexOfThings][1]#end of level 1-1

	for row in reader:
		if readIt:
			frameIndex = int(row[0])
			if frameIndex<maxFrame and frameIndex>=minFrameIndex:#For testing purposes
				if not frameIndex in changeFrames.keys():
					changeFrames[frameIndex] = Frame(frameIndex)
				changeFrames[frameIndex].AddRow(row, True)
			elif frameIndex>maxFrame:
				break

		readIt = True

	source.close()

	#Sprite Changes
	source = open(spriteAccelerationCSV,"rb")
	reader = csv.reader(source)

	readIt = False

	for row in reader:
		if readIt:
			frameIndex = int(row[0])
			if frameIndex<maxFrame and frameIndex>=minFrameIndex:#For testing purposes
				if not frameIndex in changeFrames.keys():
					changeFrames[frameIndex] = Frame(frameIndex)
				changeFrames[frameIndex].AddRow(row)
			elif frameIndex>maxFrame:
				break

		readIt = True

	source.close()
	

	#Sprite Static
	print ("Sprite static")
	source = open(spritesCSV,"rb")
	reader = csv.reader(source)

	readIt = False

	for row in reader:
		if readIt:
			frameIndex = int(row[0])
			if frameIndex<maxFrame and frameIndex>=minFrameIndex:#For testing purposes
				if not frameIndex in changeFrames.keys():
					changeFrames[frameIndex] = Frame(frameIndex)
				changeFrames[frameIndex].AddRow(row)
			else:
				break
		readIt = True

	source.close()
	

	#Get Camera Positions
	print ("Camera pos")
	source = open(cameraPositions[indexOfThings],"rb")
	reader = csv.reader(source)

	prevCameraX = 0
	prevCameraY = 0
	for row in reader:
		if int(row[0])<maxFrame and int(row[0])>=minFrameIndex:
			changeFrames[int(row[0])].SetCameraX(int(row[1]), prevCameraX)
			changeFrames[int(row[0])].SetCameraY(int(row[1]), prevCameraY)
			prevCameraX = int(row[1])
			prevCameraY = int(row[2])

	source.close()

	#Create initial Engine
	currEngine = pickle.load(open("./Engines/partialEngine33418.p", "rb"))


	notDone = True
	currIndex = minFrameIndex+1
	prevFrame = changeFrames[minFrameIndex]
	visitedEngineList = []
	
	currFurthestFrame = minFrameIndex
	currBestEngine = None
	skippableFrames = []
	while notDone:
		print ("Curr Index: "+str(currIndex))
		#Check if we're done
		if currIndex==maxFrame:#1788:
			notDone = False
			break

		

		#Predict from last frame
		newFrames = Predict(prevFrame, currEngine, changeFrames[currIndex])
		foundFrame = False


		for frame in newFrames:
			frame.frameScreen = {}
			thisDist = FrameDistance(frame, changeFrames[currIndex])
			#print "    Check Dist: "+str(thisDist)+". Player: "+str(frame.player)+" vs "+str(changeFrames[currIndex].player)
			#print "This Dist: "+str(thisDist)
			if thisDist==0 or currIndex in skippableFrames:#Less than 5% off 7571.2  1%: 1514.24	0.5%: 757	0.05%: 76	
				#if currIndex>currFurthestFrame:
				#	print "NEW BEST"
				#	currFurthestFrame = currIndex
				#	currBestEngine = currEngine	
				prevFrame = frame#changeFrames[currIndex]#frame#changeFrames[currIndex] #TODO; put this back if this doesn't work
				currIndex+=1
				foundFrame = True

				if not frame.player==None:
					if changeFrames[currIndex].player==None or changeFrames[currIndex-1].player==None or frame.player.x!=changeFrames[currIndex].player.x or frame.player.y!=changeFrames[currIndex].player.y:
						prevFrame = changeFrames[currIndex-1]


				break



		#for condition in newFrames[0].ReallyGetConditions():
		#	print "  Attempt Condition: "+str(condition)

		#for condition in changeFrames[currIndex].ReallyGetConditions():
		#	print "  Goal Condition: "+str(condition)

		#for frameObj in prevFrame.frameObjects:
		#	print "  Prev Obj: "+str(frameObj)

		#for frameObj in changeFrames[currIndex].frameObjects:
		#	print "  Goal Obj: "+str(frameObj)

		
		
		if not foundFrame:
			#if currIndex<currFurthestFrame:
			#	print "SETTING TO CURR BEST ENGINE FROM FRAME: "+str(currIndex)+" vs "+str(currFurthestFrame)
			#	currEngine = currBestEngine

			#Learn and reset
			notLearned = True
			engineQueueList = []
			engineQueue = PriorityQueue(0)
			engineQueue.put([0, EngineNode(None, currEngine)])

			notLearnedIterations = 0
			bestEngineThisAttempt = None
			bestEngineScoreThisAttempt = float("inf")
			while notLearned:
				print "Not Learned Iterations: "+str(notLearnedIterations)
				notLearnedIterations += 1

				#if notLearnedIterations>5:
				#	currEngine = engineCheckNode.engine
				#	break

				#Search algorithm. A*???
				engineCheckNode = engineQueue.get()[1]
				visitedEngineList.append(engineCheckNode.engine)
				currEngine = engineCheckNode.engine
				#print "Engine Queue Size: "+str((engineQueue.qsize()))
				#print "New Engine Check Node: "+str(engineCheckNode.GetTotalDistance())
				#for rule in engineCheckNode.engine.rules:
				#	print "   Normal "+str(rule)
				#for rule in engineCheckNode.engine.controlRules:
				#	print "   Control "+str(rule)

				#Check and see if we made it
				newFrames = Predict(prevFrame, engineCheckNode.engine, changeFrames[currIndex])
				currConditionSet = []
				minFrame = None
				minFrameDist = float("inf")
				for frame in newFrames:
					#Check and see if we're close enough
					frameDist = FrameDistance(frame, changeFrames[currIndex])
					print "Frame Dist: "+str(frameDist)

					if frameDist<minFrameDist:
						minFrameDist = frameDist
						minFrame = frame

						if bestEngineScoreThisAttempt>minFrameDist:
							bestEngineScoreThisAttempt = minFrameDist
							bestEngineThisAttempt = engineCheckNode.engine


					if frameDist==0:#Less than 0.5% off 0.05%: 76
						currEngine = engineCheckNode.engine
						notLearned = False
						break

				if notLearned:


					currConditionSet = list(minFrame.ReallyGetConditions())
					postVelocityFrames = PhysicsPredict(prevFrame, engineCheckNode.engine, changeFrames[currIndex])
					postVelocityConditionSet = None
					for frame in postVelocityFrames:
						if postVelocityConditionSet == None:
							postVelocityConditionSet = set(frame.ReallyGetConditions())
						else:
							postVelocityConditionSet = postVelocityConditionSet.intersection(frame.ReallyGetConditions())


					#print "Min Player Pos: "+str(minFrame.player)
					#print "Goal Player Pos: "+str(changeFrames[currIndex].player)
					#print "Prev Player Pos: "+str(prevFrame.player)
					#Make sure it's reset to before rules were acted upon it
					prevFrame.conditions = []
					prevFrameSet = list(prevFrame.ReallyGetConditions())
					goalConditionSet = set(changeFrames[currIndex].ReallyGetConditions())#set(changeFrames[currIndex].ReallyGetConditions()).difference(currConditionSet)
					#Transition Function: Generate new engines from this engine
					#How to pick the rules to add?
					#Modifiction Rules

					#for condition in prevFrame.ReallyGetConditions():
					#	print "PREV CONDITION: "+str(condition)
					#print ""
					#for goalCondition in changeFrames[currIndex].ReallyGetConditions():
					#	print "GOAL CONDITION: "+str(goalCondition)
					
					newEngineList = []
					#what if each rule's conditions weren't present? would that help? 
					#If yes, find the union of the conditions here and for the rule
					for rule in engineCheckNode.engine.totalRules:
						#If the rule was not triggered
						#print "Rule was not triggered: "+str(rule)
						removedConditionRule = rule.clone()
						for preReq in removedConditionRule.preconditions:
							preReq.changeConditions = []
						#If it did get activated, would that be helpful?
						possibleFrame = removedConditionRule.Activate(RulePrecondition([rule.change[0]], rule.change[0].frameObject), prevFrame)

						possibleConditionsSet = set(possibleFrame.ReallyGetConditions())

						#Remove the things that are the same in the prev frame
						possibleConditionsSet=possibleConditionsSet.difference(prevFrameSet)

						#print "Possible Improvement: "+str(len(possibleConditionsSet.intersection(goalConditionSet)))
						#Modify this rule if it gives us goal conditions we didn't have before
						if len(possibleConditionsSet.intersection(goalConditionSet))!=0:

							modifyEngine = Engine(currEngine)
							usefulModification = False
							for precogIndex in range(0, len(rule.preconditions)):
								unionSet = set(rule.preconditions[precogIndex].conditionList).intersection(set(prevFrameSet).intersection(currConditionSet))
								if not len(unionSet) == 0:
									newRule = rule.clone()
									newRule.preconditions[precogIndex] = RulePrecondition(list(unionSet), newRule.change[0].frameObject)
									modifyEngine.ReplaceRule(rule, newRule, engineCheckNode.engine)
									usefulModification = True
									break

							if usefulModification:
								newEngineList.append(modifyEngine)
							else:
								#Extend rule to another case
								newRule = rule.clone()
								newRule.preconditions.append(RulePrecondition(list(set(prevFrameSet).intersection(currConditionSet)), newRule.change[0].frameObject))
								modifyEngine.ReplaceRule(rule, newRule, engineCheckNode.engine)
								newEngineList.append(modifyEngine)

						#Regardless if rule was triggered, what if it had been applied to a diff condition with same effects
						#What if we switched out the values of an existant rule?
						#Do we need a obj to obj matching to do this? no
						
						for spriteName in prevFrame.spritesContained:
							potentialRule = rule.clone()
							if not isinstance(potentialRule.change[0], VariableCondition):
								toSwapOut = potentialRule.change[0].spriteName
								if spriteName!=toSwapOut:
									for prereq in potentialRule.preconditions:
										for condition in prereq.conditionList: 
											if not isinstance(condition, VariableCondition):
												if condition.spriteName==toSwapOut:
													condition.spriteName = spriteName
								potentialRule.change[0].spriteName = spriteName

								#If this modified rule had been activated, would that have been helpful?
								possibleFrame = potentialRule.Activate(RulePrecondition([potentialRule.change[0]], potentialRule.change[0].frameObject), prevFrame)

								possibleConditionsSet = set(possibleFrame.ReallyGetConditions())

								#Remove the things that are the same in the prev frame
								possibleConditionsSet=possibleConditionsSet.difference(prevFrameSet) 

								#
								if len(possibleConditionsSet.intersection(goalConditionSet))!=0:
									modifyEngine = Engine(currEngine)
									if not potentialRule in modifyEngine.rules:
										modifyEngine.AddRule(potentialRule, prevFrame, changeFrames[currIndex])
										if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
											newEngineList.append(modifyEngine)

						#What if we made the rule based on control input
						if rule.change[0].isPlayerRule and (rule in engineCheckNode.engine.rules):
							#TODO; check if this would help?
							modifyEngine = Engine(engineCheckNode.engine)
							modifyEngine.rules.remove(rule)
							modifyEngine.controlRules.append(rule)
							newEngineList.append(modifyEngine)
							
						

					handledConditions = []
					#Check if something should appear
					for goalCondition in goalConditionSet:
						if isinstance(goalCondition, AnimationCondition):
							#can't have two players
							if not goalCondition.frameObject in minFrame.frameObjects and (not "mario" in goalCondition.spriteName or ("mario" in goalCondition.spriteName and not "mario" in minFrame.spritesContained)) :
								newRule = Rule([RulePrecondition(list(currConditionSet), minFrame.player)], [AnimationCondition(None, "None"), goalCondition])
								modifyEngine = Engine(currEngine)
								if not newRule in modifyEngine.rules:
									modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
									if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
										newEngineList.append(modifyEngine)
										handledConditions.append(goalCondition)


					#Check for velocity rules
					for condition in prevFrameSet:
						if isinstance(condition, VelocityXCondition):
							for goalCondition in goalConditionSet:
								if isinstance(goalCondition, VelocityXCondition):
									if goalCondition.spriteName==condition.spriteName and not goalCondition.velocityValue==condition.velocityValue:
										newRule = Rule([RulePrecondition(list(postVelocityConditionSet), condition.frameObject)], [condition, goalCondition])
										modifyEngine = Engine(currEngine)
										
										#if goalCondition.spriteName=="largeHill":
										#	print "Attempting to add rule: "+str(newRule)+" for obj "+str(condition.frameObject)
										if not newRule in modifyEngine.rules:
											#if goalCondition.spriteName=="largeHill":
											#	print "Rule was not in engine"

											modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
											if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
												#if goalCondition.spriteName=="largeHill":
												#	print "Engine was not in lists"
												newEngineList.append(modifyEngine)
												handledConditions.append(condition)
						elif isinstance(condition, VelocityYCondition):
							for goalCondition in goalConditionSet:
								if isinstance(goalCondition, VelocityYCondition):
									if goalCondition.spriteName==condition.spriteName and not goalCondition.velocityValue==condition.velocityValue:
										newRule = Rule([RulePrecondition(list(postVelocityConditionSet), condition.frameObject)], [condition, goalCondition])
										modifyEngine = Engine(currEngine)
										if not newRule in modifyEngine.rules:
											modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
											if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
												newEngineList.append(modifyEngine)
												handledConditions.append(condition)

					#Check all other rules to add
					for condition in currConditionSet:
						#Check if something should disappear
						if isinstance(condition, AnimationCondition):
							if not condition.frameObject in changeFrames[currIndex].frameObjects and (not "mario" in condition.spriteName or ("mario" in condition.spriteName and changeFrames[currIndex].player==None)):
								newRule = Rule([RulePrecondition(list(currConditionSet), condition.frameObject)], [condition, AnimationCondition(None, "None")])
								modifyEngine = Engine(currEngine)
								if not newRule in modifyEngine.rules:
									modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
									if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
										newEngineList.append(modifyEngine)
										handledConditions.append(condition)

						for goalCondition in goalConditionSet:
							if type(condition) is type(goalCondition):
								if not condition in handledConditions and not goalCondition in handledConditions:
									if isinstance(condition, VariableCondition):
										if condition.variableValue!=goalCondition.variableValue:
											newRule = Rule([RulePrecondition(list(currConditionSet), condition.frameObject)], [condition, goalCondition])
											modifyEngine = Engine(currEngine)
											if not newRule in modifyEngine.rules:
												modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
												if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
													newEngineList.append(modifyEngine)
									elif isinstance (condition, AnimationCondition):
										if (condition.spriteName!=goalCondition.spriteName and abs(condition.x-goalCondition.x)==0 and abs(condition.y-goalCondition.y)==0) or (condition.spriteName==goalCondition.spriteName and (condition.width!=goalCondition.width or condition.height!=goalCondition.height)):
											newRule = Rule([RulePrecondition(list(currConditionSet), condition.frameObject)], [condition, goalCondition])
											modifyEngine = Engine(currEngine)
											if not newRule in modifyEngine.rules:
												modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
												if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
													newEngineList.append(modifyEngine)
									elif isinstance(condition, SpatialCondition):
										if condition.spriteName==goalCondition.spriteName and not condition.screenPosition==goalCondition.screenPosition and abs(condition.screenPosition[0]-goalCondition.screenPosition[0])<26 and abs(condition.screenPosition[1]-goalCondition.screenPosition[1])<26:
											newRule = Rule([RulePrecondition(list(currConditionSet), condition.frameObject)], [condition, goalCondition])
											modifyEngine = Engine(currEngine)
											if not newRule in modifyEngine.rules:
												modifyEngine.AddRule(newRule, prevFrame, changeFrames[currIndex])
												if not modifyEngine in visitedEngineList and not modifyEngine in newEngineList:
													newEngineList.append(modifyEngine)
									


					#Add new engine nodes (what heuristic to use?)
					print "New Engine List Length: "+str(len(newEngineList))
					for potentialEngine in newEngineList:
						if not potentialEngine in engineQueueList:							
							newFrames = Predict(prevFrame, potentialEngine, changeFrames[currIndex])
							#prevToPredictedDiff = thisConditionSet.difference(prevFrameSet)
							minDist = float("inf")
							closestFrame = None

							for frame in newFrames:
								thisDist = FrameDistance(frame, changeFrames[currIndex])

								if thisDist<minDist:
									minDist = thisDist
									thisConditionSet = set(frame.GetFrameConditions())
									closestFrame = frame
							


							totalDifference = len(goalConditionSet.symmetric_difference(thisConditionSet))
							totalDifference += minDist+len(potentialEngine.totalRules)
							
							if minDist==0:
								visitedEngineList.append(potentialEngine)
								engineNode = EngineNode(engineCheckNode, potentialEngine, int(totalDifference))
								engineQueue.put([int(minDist), engineNode])#Greedy
								engineQueueList.append(potentialEngine)
							else:
								#print "  Potential Engine: "+str(newEngineList.index(potentialEngine))+" of "+str(len(newEngineList))+" total different: "+str([len(goalConditionSet.symmetric_difference(thisConditionSet)), minDist,len(potentialEngine.totalRules) ])+" with rules: "+str(len(potentialEngine.totalRules))
								#print "  Total Difference: "+str(totalDifference)
								#for goalCondition in goalConditionSet:
								#	if not goalCondition in thisConditionSet:
								#		print "    Goal "+str(goalCondition)
								#for condition in thisConditionSet:
								#	if not condition in goalConditionSet:
								#		print "    Condition "+str(condition)
								#print "  New Frames Length: "+str(len(newFrames))
								#print "      prevFrame Mario: "+str(prevFrame.player)
								#print "      predictedFrame Mario: "+str(closestFrame.player)
								#print "      goalFrame Mario: "+str(changeFrames[currIndex].player)
								#for rule in potentialEngine.rules:
								#	print "       Normal "+str(rule)
								#for rule in potentialEngine.controlRules:
								#	print "       Control "+str(rule)
								#for goalObj in changeFrames[currIndex].frameObjects:
								#	print "       Goal: "+str(goalObj)
								#print ""
								#for expectObj in closestFrame.frameObjects:
								#	print "       Expected: "+str(expectObj)

								#print "         Player: "+str(closestFrame.player)

								engineNode = EngineNode(engineCheckNode, potentialEngine, int(totalDifference))
								engineQueue.put([int(totalDifference), engineNode])#Greedy
								engineQueueList.append(potentialEngine)

			
			if not notLearned:
				currIndex = minFrameIndex+1
				prevFrame = changeFrames[minFrameIndex]
				print ""
			else:
				skippableFrames.append(currIndex)
				prevFrame = changeFrames[currIndex]
				currIndex+= 1


		if currIndex>currFurthestFrame:
			print "New Furthest Frame: "+str(currIndex)
			currFurthestFrame = currIndex
			if (currFurthestFrame-minFrameIndex)%10==0:#each 1%
				pickle.dump(currEngine, open("./Engines/partialEngine"+str(currIndex)+".p", "wb"))
	pickle.dump(currEngine, open("./Engines/finalEngine"+str(maxFrame-1)+".p", "wb"))

