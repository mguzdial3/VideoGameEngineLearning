import csv, shutil, sys, os, copy, glob, pickle
sys.path.append('/usr/local/lib/python2.7/site-packages')
import random, math
import numpy as np
from Queue import PriorityQueue
from velocityEngineLearningTest import *
import numpy as np

mergeEngine = Engine(None)
for fileVal in glob.glob("./MarioEngines/*.p"):
	print (fileVal)
	fileOpened = open(fileVal, "rb")
	engine = pickle.load(fileOpened)

	for rule in engine.rules:
		mergeAble = False
		ruleToMergeWith = None
		#Normal Rule
		for rule2 in mergeEngine.rules:
			if rule2.change[1]==rule.change[1]:
				mergeAble = True
				ruleToMergeWith = rule2
		if not mergeAble:
			mergeEngine.rules.append(rule)
			mergeEngine.totalRules.append(rule)
		else:
			mergeEngine.rules.remove(ruleToMergeWith)
			mergeEngine.totalRules.remove(ruleToMergeWith)
			ruleToMergeWith = ruleToMergeWith.clone()
			#Just straight up merge everything
			if len(rule.preconditions)==1 and len(ruleToMergeWith.preconditions)==1:
				ruleMergePrecog = ruleToMergeWith.preconditions[0]
				ruleToMergeWith.preconditions.remove(ruleMergePrecog)

				finalConditionsSet = set(ruleMergePrecog.conditionList).intersection(rule.preconditions[0].conditionList)
				finalChangeConditionSet = set(ruleMergePrecog.changeConditions).intersection(rule.preconditions[0].changeConditions)
				ruleMergePrecog.conditionList = list(finalConditionsSet)
				ruleMergePrecog.changeConditions = list(finalChangeConditionSet)
				ruleToMergeWith.preconditions = [ruleMergePrecog]
			else:
				#Find merges that work
				for precondition in rule.preconditions:
					ruleToMergeWith.preconditions.append(precondition)
			mergeEngine.rules.append(ruleToMergeWith)
			mergeEngine.totalRules.append(ruleToMergeWith)
	#Control Rule
	for rule in engine.controlRules:
		mergeAble = False
		ruleToMergeWith = None
		for rule2 in mergeEngine.controlRules:
			if rule2.change[1]==rule.change[1]:
				mergeAble = True
				ruleToMergeWith = rule2
		if not mergeAble:
			mergeEngine.controlRules.append(rule)
			mergeEngine.totalRules.append(rule)
		else:
			mergeEngine.controlRules.remove(ruleToMergeWith)
			mergeEngine.totalRules.remove(ruleToMergeWith)
			ruleToMergeWith = ruleToMergeWith.clone()
			#Just straight up merge everything
			if len(rule.preconditions)==1 and len(ruleToMergeWith.preconditions)==1:
				ruleMergePrecog = ruleToMergeWith.preconditions[0]
				ruleToMergeWith.preconditions.remove(ruleMergePrecog)

				finalConditionsSet = set(ruleMergePrecog.conditionList).intersection(rule.preconditions[0].conditionList)
				finalChangeConditionSet = set(ruleMergePrecog.changeConditions).intersection(rule.preconditions[0].changeConditions)
				ruleMergePrecog.conditionList = list(finalConditionsSet)
				ruleMergePrecog.changeConditions = list(finalChangeConditionSet)
				ruleToMergeWith.preconditions = [ruleMergePrecog]
			else:
				#Find merges that work
				for precondition in rule.preconditions:
					ruleToMergeWith.preconditions.append(precondition)
			mergeEngine.controlRules.append(ruleToMergeWith)
			mergeEngine.totalRules.append(ruleToMergeWith)

for fileVal in glob.glob("./Engines/*.p"):
	print (fileVal)
	fileOpened = open(fileVal, "rb")
	engine = pickle.load(fileOpened)

	for rule in engine.rules:
		mergeAble = False
		ruleToMergeWith = None
		#Normal Rule
		for rule2 in mergeEngine.rules:
			if rule2.change[1]==rule.change[1]:
				mergeAble = True
				ruleToMergeWith = rule2
		if not mergeAble:
			mergeEngine.rules.append(rule)
			mergeEngine.totalRules.append(rule)
		else:
			mergeEngine.rules.remove(ruleToMergeWith)
			mergeEngine.totalRules.remove(ruleToMergeWith)
			ruleToMergeWith = ruleToMergeWith.clone()
			#Just straight up merge everything
			if len(rule.preconditions)==1 and len(ruleToMergeWith.preconditions)==1:
				ruleMergePrecog = ruleToMergeWith.preconditions[0]
				ruleToMergeWith.preconditions.remove(ruleMergePrecog)

				finalConditionsSet = set(ruleMergePrecog.conditionList).intersection(rule.preconditions[0].conditionList)
				finalChangeConditionSet = set(ruleMergePrecog.changeConditions).intersection(rule.preconditions[0].changeConditions)
				ruleMergePrecog.conditionList = list(finalConditionsSet)
				ruleMergePrecog.changeConditions = list(finalChangeConditionSet)
				ruleToMergeWith.preconditions = [ruleMergePrecog]
			else:
				#Find merges that work
				for precondition in rule.preconditions:
					ruleToMergeWith.preconditions.append(precondition)
			mergeEngine.rules.append(ruleToMergeWith)
			mergeEngine.totalRules.append(ruleToMergeWith)
	#Control Rule
	for rule in engine.controlRules:
		mergeAble = False
		ruleToMergeWith = None
		for rule2 in mergeEngine.controlRules:
			if rule2.change[1]==rule.change[1]:
				mergeAble = True
				ruleToMergeWith = rule2
		if not mergeAble:
			mergeEngine.controlRules.append(rule)
			mergeEngine.totalRules.append(rule)
		else:
			mergeEngine.controlRules.remove(ruleToMergeWith)
			mergeEngine.totalRules.remove(ruleToMergeWith)
			ruleToMergeWith = ruleToMergeWith.clone()
			#Just straight up merge everything
			if len(rule.preconditions)==1 and len(ruleToMergeWith.preconditions)==1:
				ruleMergePrecog = ruleToMergeWith.preconditions[0]
				ruleToMergeWith.preconditions.remove(ruleMergePrecog)

				finalConditionsSet = set(ruleMergePrecog.conditionList).intersection(rule.preconditions[0].conditionList)
				finalChangeConditionSet = set(ruleMergePrecog.changeConditions).intersection(rule.preconditions[0].changeConditions)
				ruleMergePrecog.conditionList = list(finalConditionsSet)
				ruleMergePrecog.changeConditions = list(finalChangeConditionSet)
				ruleToMergeWith.preconditions = [ruleMergePrecog]
			else:
				#Find merges that work
				for precondition in rule.preconditions:
					ruleToMergeWith.preconditions.append(precondition)
			mergeEngine.controlRules.append(ruleToMergeWith)
			mergeEngine.totalRules.append(ruleToMergeWith)

#for rule in mergeEngine.rules:
#	print "Normal Rule: "+str(rule)




for controlRule in mergeEngine.controlRules:
	print "Control Rule: "+str(controlRule)
	for condition in controlRule.preconditions[0].conditionList:
		if isinstance(condition, SpatialCondition):
			print "    "+str(condition)
		elif isinstance(condition, VelocityXCondition) or isinstance(condition, VelocityYCondition):
			print "    "+str(condition)
	