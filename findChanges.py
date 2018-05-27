import csv, shutil, sys, os, copy, glob
import random, math
import numpy as np

frameDirectory = ""#"./AdamLevels-Processed/GameplayVideo3Source/AllFrameDescriptions"
playerFrames = "./Longplay3/megaman.csv"#"marioFramesAll.csv"
spriteFrames = "./Longplay3/spriteDescripts.csv"#"frameDescriptionColorAll.csv"

playerVelocityFrames ="./Longplay3/playerChanges.csv"#"marioChanges.csv"
spriteVelocityFrames = "./Longplay3/spriteChanges.csv"#"spriteChanges.csv"

playerAccelerationFrames = "./Longplay3/playerAccelerationTrack.csv"#"playerAccelerationTrack.csv"
spriteAccelerationFrames = "./Longplay3/spriteAccelerationTrack.csv"#"spriteAccelerationTrack.csv"

#TODO; read these in #3: 512, 5300 #5: 33368, 38847
startFrame = 512
endFrame = 5300

#The thing for storing a reference to a single object in a frame
class FrameObject:
	def __init__(self, name, positionX, positionY, width, height, confidence):
		self.name = name
		self.x = positionX
		self.y = positionY
		self.width = width
		self.height = height
		self.confidence = confidence
		self.centerX = positionX+self.width/2.0
		self.centerY = positionY+self.height/2.0
		self.velocity = (0,0)

	def setVelocity(self, newVelocity):
		self.velocity = newVelocity


#Parse the spritenames to clean them up a bit
def parseSpritename(strVal):
	backgroundSignifiers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "L", "R"]

	#Remove .png characters
	if ".png" in strVal:
		index = strVal.find(".png")
		if not index==-1:
			strVal = strVal[:index]

	#Remove all background signifiers
	if strVal[len(strVal)-1] in backgroundSignifiers:
		strVal = strVal[:len(strVal)-1]

	return strVal

#Return distance between two objects in terms of centroid distance and dimensions difference
def objectDistance(obj1, obj2):
	return abs(obj1.centerX-obj2.centerX) + abs(obj1.centerY-obj2.centerY) + abs( (obj1.width)-(obj2.width) )+abs(obj1.height-obj2.height)

spriteNames = []
#Make sure we only use sprites that are acceptable
directory = "./sprites/"
for subDirectory in os.walk(directory):
	for filename in glob.glob(str(subDirectory[0])+"/*.png"):
		
		spritename = filename.split("/")[2]
		if not spritename in spriteNames:
			spriteNames.append(spritename)



#Load in all information for each frame
frameInfo = {}

source = open(frameDirectory+spriteFrames,"rb")
reader = csv.reader(source)

readIt = False
currFrame = startFrame
currObjects = []

for row in reader:
	if readIt:
		potentialFrame = int(row[0])
		if not currFrame==potentialFrame:
			#Store the entire list of objects 
			frameInfo[currFrame] = currObjects
			currObjects = []
			currFrame = potentialFrame
		else:
			nameOfSprite = str(row[1])

			if nameOfSprite in spriteNames:
				nameOfSprite = parseSpritename(nameOfSprite)
				# add this to our current list of objects at this frame
				currObjects.append(FrameObject(nameOfSprite, int(row[2]), int(row[3]), int(row[5]), int(row[4]), float(row[6]) ))
	readIt=True

#Load all the marios for each frame
marioInfo = {}

source = open(frameDirectory+playerFrames,"rb")
reader = csv.reader(source)

readIt = False

for row in reader:
	if readIt:
		potentialFrame = int(row[0])
		
		nameOfSprite = str(row[1])
		if not "None" in nameOfSprite:
			nameOfSprite = parseSpritename(nameOfSprite)
			# add this to our current list of objects at this frame
			marioInfo[potentialFrame] = FrameObject(nameOfSprite, int(row[2]), int(row[3]), int(row[5]), int(row[4]), float(row[6]) )
		else:
			marioInfo[potentialFrame] = None
	readIt=True


#Non-player sprite changes

target = open(frameDirectory+spriteVelocityFrames,"wr")
writer = csv.writer(target)
rowOne = ["frame", "prevSprite", "thisSprite", "x", "y", "width", "height", "velocityX", "velocityY", "changeConfidence"]
writer.writerow(rowOne)
for frame in range(startFrame, endFrame+1):
	print "Frame: "+str(frame)
	#First detect changes in the non-player sprite infos
	if frame in frameInfo.keys():
		preFrame = frame -1
		
		if preFrame in frameInfo.keys():#Looking for velocity or sprite changes
			#Look for every object for all kinds of changes

			#Create all pairs
			frameObjects = frameInfo[frame]
			preFrameObjects = frameInfo[preFrame]

			#Sort both of the lists
			frameObjects = sorted(frameObjects, key = lambda item: (item.centerX, item.centerY, item.width, item.height))
			preFrameObjects = sorted(preFrameObjects, key = lambda item: (item.centerX, item.centerY, item.width, item.height))

			fromObjects = []
			toObjects = []

			#Determine where we'll pulling from based on 
			if len(frameObjects)>=len(preFrameObjects):
				fromObjects = frameObjects
				toObjects = preFrameObjects
			else:
				fromObjects = preFrameObjects
				toObjects = frameObjects

			maxLength = max(len(frameObjects), len(preFrameObjects))
			fromPairs = fromObjects
			toPairs = [None]*maxLength
			toDists = [float("inf")]*maxLength

			pairIndex = 0
			threshold = 60

			#Do the match up
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

			#Get max list for determine the best pairing 
			prevEndPair = [None]*maxLength
			currEndPair = [None]*maxLength

			if len(frameObjects)>=len(preFrameObjects):
				currEndPair = frameObjects
				prevEndPair = toPairs
			else:
				currEndPair = toPairs
				prevEndPair = preFrameObjects

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
				preConfidence = 1.0
				thisConfidence = 1.0
				changeConfidence = 0.0

				if not currEndPair[index]==None:
					currObj = currEndPair[index]
					thisSprite = currObj.name
					x = currObj.centerX
					y = currObj.centerY
					width = currObj.width
					height = currObj.height
					thisConfidence = currObj.confidence

				if not prevEndPair[index]==None:
					prevObj = prevEndPair[index]
					prevSprite = prevObj.name
					preX = prevObj.centerX
					preY = prevObj.centerY
					preConfidence = prevObj.confidence

				if currEndPair[index] == None:
					x = preX
					y = preY

				if prevEndPair[index] == None:
					preX = x
					preY = y

				velocityX = x-preX
				velocityY = y-preY
				thisConfidence = obj.confidence
				changeConfidence = (preConfidence+thisConfidence)/2.0
				writer.writerow([str(frame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(changeConfidence)])



			'''
			#Determine the ideal pairing
			prevEndPair = [None]* len(maxList)
			currEndPair = [None]* len(maxList)
			pairIndex = 0

			for frameObject in maxList:
				prevObject = None
				currObject = None

				if frameObject in currToPrevPairs:
					prevIndex = currToPrevPairs.index(frameObject)
					prevDist = currToPrevDists[prevIndex]
					prevObject = currToPrevPairs[]
			'''


		else:
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
			preConfidence = 1.0
			thisConfidence = 1.0
			changeConfidence = 0.0

			#Everything in this frame appeared
			for obj in frameInfo[frame]:
				thisSprite = obj.name
				x = obj.centerX
				y = obj.centerY
				width = obj.width
				height = obj.height
				velocityX = 0#x-preX
				velocityY = 0#y-preY
				thisConfidence = obj.confidence
				changeConfidence = (preConfidence+thisConfidence)/2.0
				writer.writerow([str(frame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(changeConfidence)])


	else:
		#Did stuff dissapear
		preFrame = frame -1
		if preFrame in frameInfo.keys():
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
			preConfidence = 1.0
			thisConfidence = 1.0
			changeConfidence = 0.0
			#Everything in the previous frame disappeared
			for prevObj in frameInfo[preFrame]:
				prevSprite = prevObj.name
				preX = prevObj.centerX
				preY = prevObj.centerY
				x = preX #make the assumption that we disappear in the same position
				y = preY #make the assumption that we disappear in the same position
				velocityX = 0#x-preX
				velocityY = 0#y-preY
				preConfidence = prevObj.confidence
				changeConfidence = (preConfidence+thisConfidence)/2.0
				writer.writerow([str(frame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(changeConfidence)])
target.close()

##Next detect player changes
target = open(frameDirectory+playerVelocityFrames,"wr")
writer = csv.writer(target)
rowOne = ["frame", "prevSprite", "thisSprite", "x", "y", "width", "height", "velocityX", "velocityY", "changeConfidence"]
writer.writerow(rowOne)
for frame in range(startFrame, endFrame+1):
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
	preConfidence = 1.0
	thisConfidence = 1.0
	changeConfidence = 0.0

	preFrame = frame-1
	if preFrame in marioInfo.keys() and not marioInfo[preFrame] ==None:
		prevSprite = marioInfo[preFrame].name
		preX = marioInfo[preFrame].centerX
		preY = marioInfo[preFrame].centerY
		preConfidence = marioInfo[preFrame].confidence
	elif frame in marioInfo.keys() and not marioInfo[frame]==None:
		obj = marioInfo[frame]
		preX = obj.x
		preY = obj.y

	if frame in marioInfo.keys() and not marioInfo[frame]==None:
		obj = marioInfo[frame]
		thisSprite = obj.name
		x = obj.centerX
		y = obj.centerY
		width = obj.width
		height = obj.height
		thisConfidence = obj.confidence
	elif preFrame in marioInfo.keys() and not marioInfo[preFrame] ==None:
		x = preX
		y = preY


	changeConfidence = (preConfidence+thisConfidence)/2.0
	velocityX = x-preX
	velocityY = y - preY

	writer.writerow([str(frame), prevSprite, thisSprite, str(x), str(y), str(width), str(height), str(velocityX), str(velocityY), str(changeConfidence)])

target.close()

#ACCELERATION CHANGES CALCULATE

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
source = open(frameDirectory+playerVelocityFrames,"rb")
reader = csv.reader(source)

target = open(frameDirectory+playerAccelerationFrames, "wr")
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
source = open(frameDirectory+spriteVelocityFrames,"rb")
reader = csv.reader(source)

target = open(frameDirectory+spriteAccelerationFrames, "wr")
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




