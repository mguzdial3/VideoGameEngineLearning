import csv, shutil, sys, os, copy, glob
import random, math
import numpy as np

frameDirectory = "./frames5-25fpers/"


#The thing for storing a reference to a single object in a frame
class FrameObject:
	def __init__(self, name, positionX, positionY, width, height, velocityX, velocityY, confidence):
		self.name = name
		self.width = width
		self.height = height
		self.confidence = confidence
		self.centerX = positionX
		self.centerY = positionY
		self.velocity = (velocityX,velocityY)


#Return distance between two objects in terms of centroid distance and dimensions difference
def objectDistance(obj1, obj2):
	return abs(obj1.centerX-obj2.centerX) + abs(obj1.centerY-obj2.centerY) + abs( (obj1.width)-(obj2.width) )+abs(obj1.height-obj2.height) + abs(obj1.velocity[0]-obj2.velocity[0]) + abs(obj1.velocity[1]-obj2.velocity[1])


#PLAYER SHIT
source = open(frameDirectory+"marioChanges.csv","rb")
reader = csv.reader(source)

target = open("./frames5-25fpers/playerAccelerationTrack.csv", "wr")
writer = csv.writer(target)

rowOne = ["frame", "prevSprite", "thisSprite", "x", "y", "width", "height", "velocityX", "velocityY", "preVelocityX", "preVelocityY", "changeConfidence"]
writer.writerow(rowOne)
readIt = False

#Stores velocity for last frame
preVelocityX = 0
preVelocityY = 0

for row in reader:
	if readIt:
		print str(row[0])
		writer.writerow([row[0], str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7]), str(row[8]), str(preVelocityX), str(preVelocityY), str(row[9])])
		preVelocityX = float(row[7])
		preVelocityY = float(row[8])
	readIt=True

target.close()
source.close()


#OTHER SPRITES
source = open("./frames5-25fpers/spriteChanges.csv","rb")
reader = csv.reader(source)

target = open("./frames5-25fpers/spriteAccelerationTrack.csv", "wr")
writer = csv.writer(target)

rowOne = ["frame", "prevSprite", "thisSprite", "x", "y", "width", "height", "velocityX", "velocityY", "preVelocityX", "preVelocityY", "changeConfidence"]
writer.writerow(rowOne)
readIt = False

#Stores velocity for last frame
prevFrameObjects = []
thisFrameObjects = []
prevFrame = 0
thisFrame = 0

for row in reader:
	if readIt:
		currentFrame = int(row[0])
		if not currentFrame==thisFrame and len(thisFrameObjects)>0:
			print "Frame Print "+str(thisFrame)
			if len(prevFrameObjects)>0 and thisFrame==(prevFrame+1):
				#Set up for matching
				thisFrameObjects = sorted(thisFrameObjects, key = lambda item: (item.centerX, item.centerY, item.width, item.height))

				fromObjects = []
				toObjects = []

				#Determine where we'll pulling from based on 
				if len(thisFrameObjects)>=len(prevFrameObjects):
					fromObjects = thisFrameObjects
					toObjects = prevFrameObjects
				else:
					fromObjects = prevFrameObjects
					toObjects = thisFrameObjects

				maxLength = max(len(thisFrameObjects), len(prevFrameObjects))
				fromPairs = fromObjects
				toPairs = [None]*maxLength
				toDists = [float("inf")]*maxLength

				pairIndex = 0
				threshold = 70

				#Do matching from from to to
				for obj in fromObjects:
					matchFound = False
					cantUse = []
					#search till we find an unused object from prevObjects in toObjects to pair with fromObjects
					while not matchFound:
						minObj = None
						minDist = float("inf")
						for toObj in toObjects:
							thisDist = objectDistance(obj, toObj)
							if thisDist<minDist and thisDist<threshold and not toObj in cantUse:
								minObj=toObj
								minDist = thisDist

						if minObj == None:# We can't find any pair for this
							toPairs[pairIndex] = None
							pairIndex +=1 #Move to next pairIndex
							matchFound = True
						else: #We found a pair for this
							
							if not minObj in toPairs: #If this isn't already in toPairs
								toPairs[pairIndex] = minObj
								toDists[pairIndex] = thisDist
								pairIndex +=1 #Move to next pairIndex
								matchFound = True
							else: #If this is already in toPairs
								toPairIndex = toPairs.index(minObj)
								
								if toDists[toPairIndex]<=minDist: #If its already used and toDists has a better match
									cantUse.append(minObj)
								else: #If it's already used but toDists has a worse match
									#Set this value
									toPairs[pairIndex] = minObj
									toDists[pairIndex] = thisDist
									pairIndex +=1 #Move to next pairIndex
									matchFound = True

									#reset the old value
									toPairs[toPairIndex] = None
									toDists[toPairIndex] = float("inf")

									#Find a new value (if we can)
									if pairIndex<(len(toPairs)-1):
										minObj = None
										minDist = float("inf")
										for index in range(pairIndex, len(toObjects)):
											thisDist = objectDistance(fromObjects[toPairIndex], toObjects[index])
											if thisDist<minDist and thisDist<threshold:
												minObj=toObjects[index]
												minDist = thisDist
										toPairs[toPairIndex] = minObj
										toDists[toPairIndex] = minDist

				#Activate the pairs
				currEndPair = None
				prevEndPair = None
				if len(thisFrameObjects)>=len(prevFrameObjects):
					currEndPair = thisFrameObjects
					prevEndPair = toPairs
				else:
					currEndPair = toPairs
					prevEndPair = prevFrameObjects

				#Write out all the pairs
				for index in range(0, maxLength):
					prevSprite = "None"
					thisSprite = "None"
					x = 0
					y = 0
					preX = 0
					preY = 0
					width = 0
					height = 0
					velocityX  = 0
					velocityY = 0
					preVelocityX = 0
					preVelocityY = 0
					preConfidence = 1.0
					thisConfidence = 1.0
					changeConfidence = 0.0

					if not currEndPair[index]==None:
						currObj = currEndPair[index]
						thisSprite = currObj.name
						x = currObj.centerX
						y = currObj.centerY
						velocityX = currEndPair[index].velocity[0]
						velocityY = currEndPair[index].velocity[1]
						width = currObj.width
						height = currObj.height
						thisConfidence = currObj.confidence

					if not prevEndPair[index]==None:
						prevObj = prevEndPair[index]
						prevSprite = prevObj.name
						preX = prevObj.centerX
						preY = prevObj.centerY
						preVelocityX = prevEndPair[index].velocity[0]
						preVelocityY = prevEndPair[index].velocity[1]
						preConfidence = prevObj.confidence

					if currEndPair[index] == None:
						x = preX
						y = preY
						velocityX = preVelocityX
						velocityY = preVelocityY

					if prevEndPair[index] == None:
						preX = x
						preY = y
						preVelocityX = velocityX
						preVelocityY = velocityY

					thisConfidence = obj.confidence
					changeConfidence = thisConfidence
					writer.writerow([str(thisFrame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(preVelocityX), str(preVelocityY), str(changeConfidence)])


			else:
				#Print out all of them assuming no stuff
				preVelocityX = 0
				preVelocityY = 0
				for fo in thisFrameObjects:
					writer.writerow([str(thisFrame), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7]), str(row[8]), str(preVelocityX), str(preVelocityY), str(row[9])])
			prevFrameObjects = thisFrameObjects
			prevFrame = thisFrame
			thisFrameObjects = []	

		thisFrameObjects.append(FrameObject(str(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9])))
		thisFrame = currentFrame
	readIt=True

#Set up for matching
thisFrameObjects = sorted(thisFrameObjects, key = lambda item: (item.centerX, item.centerY, item.width, item.height))

fromObjects = []
toObjects = []

#Determine where we'll pulling from based on 
if len(thisFrameObjects)>=len(prevFrameObjects):
	fromObjects = thisFrameObjects
	toObjects = prevFrameObjects
else:
	fromObjects = prevFrameObjects
	toObjects = thisFrameObjects

maxLength = max(len(thisFrameObjects), len(prevFrameObjects))
fromPairs = fromObjects
toPairs = [None]*maxLength
toDists = [float("inf")]*maxLength

pairIndex = 0
threshold = 70

#Do matching from from to to
for obj in fromObjects:
	matchFound = False
	cantUse = []
	#search till we find an unused object from prevObjects in toObjects to pair with fromObjects
	while not matchFound:
		minObj = None
		minDist = float("inf")
		for toObj in toObjects:
			thisDist = objectDistance(obj, toObj)
			if thisDist<minDist and thisDist<threshold and not toObj in cantUse:
				minObj=toObj
				minDist = thisDist

		if minObj == None:# We can't find any pair for this
			toPairs[pairIndex] = None
			pairIndex +=1 #Move to next pairIndex
			matchFound = True
		else: #We found a pair for this
			
			if not minObj in toPairs: #If this isn't already in toPairs
				toPairs[pairIndex] = minObj
				toDists[pairIndex] = thisDist
				pairIndex +=1 #Move to next pairIndex
				matchFound = True
			else: #If this is already in toPairs
				toPairIndex = toPairs.index(minObj)
				
				if toDists[toPairIndex]<=minDist: #If its already used and toDists has a better match
					cantUse.append(minObj)
				else: #If it's already used but toDists has a worse match
					#Set this value
					toPairs[pairIndex] = minObj
					toDists[pairIndex] = thisDist
					pairIndex +=1 #Move to next pairIndex
					matchFound = True

					#reset the old value
					toPairs[toPairIndex] = None
					toDists[toPairIndex] = float("inf")

					#Find a new value (if we can)
					if pairIndex<(len(toPairs)-1):
						minObj = None
						minDist = float("inf")
						for index in range(pairIndex, len(toObjects)):
							thisDist = objectDistance(fromObjects[toPairIndex], toObjects[index])
							if thisDist<minDist and thisDist<threshold:
								minObj=toObjects[index]
								minDist = thisDist
						toPairs[toPairIndex] = minObj
						toDists[toPairIndex] = minDist

#Activate the pairs
currEndPair = None
prevEndPair = None
if len(thisFrameObjects)>=len(prevFrameObjects):
	currEndPair = thisFrameObjects
	prevEndPair = toPairs
else:
	currEndPair = toPairs
	prevEndPair = prevFrameObjects

#Write out all the pairs
for index in range(0, maxLength):
	prevSprite = "None"
	thisSprite = "None"
	x = 0
	y = 0
	preX = 0
	preY = 0
	width = 0
	height = 0
	velocityX  = 0
	velocityY = 0
	preVelocityX = 0
	preVelocityY = 0
	preConfidence = 1.0
	thisConfidence = 1.0
	changeConfidence = 0.0

	if not currEndPair[index]==None:
		currObj = currEndPair[index]
		thisSprite = currObj.name
		x = currObj.centerX
		y = currObj.centerY
		velocityX = currEndPair[index].velocity[0]
		velocityY = currEndPair[index].velocity[1]
		width = currObj.width
		height = currObj.height
		thisConfidence = currObj.confidence

	if not prevEndPair[index]==None:
		prevObj = prevEndPair[index]
		prevSprite = prevObj.name
		preX = prevObj.centerX
		preY = prevObj.centerY
		preVelocityX = prevEndPair[index].velocity[0]
		preVelocityY = prevEndPair[index].velocity[1]
		preConfidence = prevObj.confidence

	if currEndPair[index] == None:
		x = preX
		y = preY
		velocityX = preVelocityX
		velocityY = preVelocityY

	if prevEndPair[index] == None:
		preX = x
		preY = y
		preVelocityX = velocityX
		preVelocityY = velocityY

	thisConfidence = obj.confidence
	changeConfidence = thisConfidence
	writer.writerow([str(thisFrame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(preVelocityX), str(preVelocityY), str(changeConfidence)])

target.close()
source.close()