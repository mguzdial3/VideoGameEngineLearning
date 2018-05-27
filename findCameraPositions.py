import csv, shutil, sys, os, copy, glob, pickle
sys.path.append('/usr/local/lib/python2.7/site-packages')
import random, math
import numpy as np
from Queue import PriorityQueue

playerAccelerations = ["./Longplay5/playerAccelerationTrack.csv"]
spriteAccelerations = ["./Longplay5/spriteAccelerationTrack.csv"]
spritesListings = ["./Longplay5/spriteDescripts.csv"]
cameraPositions = "./Longplay5/cameraPositions.csv"
startAndEndFrames =[[33368, 38847]]

#3: 512, 5300 #5: 33368, 38847

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
		self.currLevel = None#Map of curr level sprites
		self.rules = []
		self.controlRules = []
		self.totalRules = []
		self.parentEngine = None
		if not parent == None:
			self.currLevel = parent.currLevel#Map of curr level sprites
			self.rules = list(parent.rules)
			self.controlRules = list(parent.controlRules)
			self.totalRules = list(self.rules+self.controlRules)
			self.parentEngine = parent

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
			if "camera" in self.change[0].variableName and not "change" in self.change[0].variableName:
				newFrame.cameraX += self.change[1].variableValue-self.change[0].variableValue
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
	backgroundSignifiers = ["S", "W", "B"]

	#Remove all background signifiers
	if spriteName[len(spriteName)-1] in backgroundSignifiers:
		spriteName = spriteName[:len(spriteName)-1]

	#TODO; remove this after animation stuff
	numberSignifiers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
	for number in numberSignifiers:
		if number in spriteName:
			spriteName = spriteName[:spriteName.index(number)]

	if "ario" in spriteName and not "ire" in spriteName:
		spriteName = "mario"

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
			return self.cameraX==other.cameraX and tuple(self.ReallyGetConditions())==tuple(other.ReallyGetConditions())
		return False

	def __ne__(self, other):
		if isinstance(other, self.__class__):
			return not self.__eq__(other)
		else:
			return True

	def __hash__(self):
		return hash(self.cameraX, tuple(self.ReallyGetConditions()))	

	def SetCameraX(self, camX, prevX):
		self.cameraX = camX
		cameraMovement = camX-prevX
		if cameraMovement>0:
			for obj in self.frameObjects:
				if not obj.velocity[0]==0:
					obj.velocity = [obj.velocity[0]+cameraMovement, obj.velocity[1]]

	def clone(self):
		cloneFrame = Frame(self.number)
		cloneFrame.cameraX = self.cameraX
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

		self.conditions.append(VariableCondition(None, "cameraPos", self.cameraX))
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

	for x in range(0,16*26):
		for y in range(0,14*26):
			if frame1.frameScreen[x][y]!=frame2.frameScreen[x][y]:
				if doPrint:
					print "   Frame Difference ("+str([x,y])+"): "+str([frame1.frameScreen[x][y], frame2.frameScreen[x][y]])
				sumDiff+=1

	return sumDiff

#Calcultes distance between frames (Hellman's metric)
def FrameDistancePercentage(frame1, frame2, changeX, changeY):
	if len(frame1.frameScreen.keys())==0:
		frame1.frameScreen = CreateFrameDict(frame1.frameObjects, frame1.player)
	if len(frame2.frameScreen.keys())==0:
		frame2.frameScreen = CreateFrameDict(frame2.frameObjects, frame2.player)

	sumDiff = 0.0

	numComparisons = 0.0

	for x in range(0,256):
		for y in range(0,224):
			if (x+changeX)>0 and (x+changeX)<(256):
				if (y+changeY)>0 and (y+changeY)<(224):
					numComparisons+=1.0
					if frame1.frameScreen[x+changeX][y+changeY]!=frame2.frameScreen[x][y]:
						sumDiff+=1.0
	finalVal = sumDiff/numComparisons
	return finalVal

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
	'''
	#Read in map
	print ("read in map")
	level1Map = {}
	with open(mapListings[indexOfThings],'r') as openFile:
		for ii in range(0,14):
			line =openFile.readline()
			level1Map[ii] = line.split(",")
	'''

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
					frameTuple = [indexOfThings, frameIndex]
					changeFrames[frameIndex] = Frame(frameTuple)
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
			if frameIndex<maxFrame:#For testing purposes
				if not frameIndex in changeFrames.keys():
					changeFrames[frameIndex] = Frame(frameIndex)
				changeFrames[frameIndex].AddRow(row)
			else:
				break
		readIt = True

	source.close()
	

	#Get Camera Positions
	print ("Camera pos")
	target = open(cameraPositions,"wr")
	writer = csv.writer(target)

	cameraPosX = 0
	cameraPosY = 0
	currFrame = minFrameIndex+1
	while currFrame<maxFrame-1:
		print "CurrFrame: "+str([currFrame, cameraPosX, cameraPosY])
		thisDiffX = 0
		thisDiffY = 0
		minDiff = 1.0

		for x in range(0,16):
			for y in range(-16,16):
				thisVal = FrameDistancePercentage(changeFrames[currFrame-1], changeFrames[currFrame],x,y)
				if thisVal<minDiff:
					minDiff = thisVal
					thisDiffX = x
					thisDiffY = y

		cameraPosX+=thisDiffX
		cameraPosY+=thisDiffY

		writer.writerow([currFrame,cameraPosX,cameraPosY])
		currFrame+=1


	