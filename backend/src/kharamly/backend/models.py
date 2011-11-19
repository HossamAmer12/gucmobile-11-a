from datetime import datetime
import urllib, json
from django.db import models
import math
# from decimal import *

# Create your models here.
# testing git reset --hard
class Node(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return str(self.id) + ":" + str(self.latitude) + ", " + str(self.longitude)

class Step(models.Model):
    html_instructions = models.TextField()
    distance_text = models.CharField(max_length=200)
    distance_value = models.IntegerField()
    duration_text = models.CharField(max_length=200)
    duration_value = models.IntegerField()
    start_location = models.ForeignKey(Node, related_name='start')
    end_location = models.ForeignKey(Node, related_name='end')

    def __unicode__(self):
        return str(self.start_location.id) + ", " + str(self.end_location.id)
    class Meta:
        ordering = ["id"]

class Step_History(models.Model):
    step = models.ForeignKey(Step, related_name='current_step')
    time = models.DateTimeField()
    speed = models.FloatField()

    def __unicode__(self):
        return str(self.step) + "," + str(self.time)

class Leg(models.Model):
    steps = models.ManyToManyField(Step)
    distance_text = models.CharField(max_length=200)
    distance_value = models.IntegerField()
    duration_text = models.CharField(max_length=200)
    duration_value = models.IntegerField()
    start_address = models.TextField()
    end_address = models.TextField()
    start_location = models.ForeignKey(Node, related_name='start_node')
    end_location = models.ForeignKey(Node, related_name='end_node')
	
    def __unicode__(self):
        return str(self.start_location) + "," + str(self.end_location)
		    

class Route(models.Model):
    summary = models.CharField(max_length=200)
    legs = models.ManyToManyField(Leg)
	
    def __unicode__(self):
        return self.summary
    
    
#####################################################################
## BUSINESS LOGIC
## IN PYTHON, IT IS ADVISED TO KEEP LOGIC IN THE MODELS
#####################################################################
#####################################################################

# Test method in model
def test_method_in_models(num):
    return num * 2

# Author : Moataz Mekki
# <sensor> & <alternatives> take the value true or false only
# <origin> & <destination> can be address or long & lat

def getdirections(origin, destination):
    url = 'http://maps.googleapis.com/maps/api/directions/json?origin=' + origin + '&destination=' + destination + '&sensor=true&alternatives=true'
    result = json.load(urllib.urlopen(url))
    routes = result['routes']
    all_routes = []
    for route in routes :
        summ = route['summary']
        legs = route['legs']
        current_route = Route(summary=summ)
        current_route.save()
        all_routes.append(current_route)
        for leg in legs :
            distance_text = leg['distance']['text']
            distance_value = leg['distance']['value']
            duration_text = leg['duration']['text']
            duration_value = leg['duration']['value']
            start_address = leg['start_address']
            end_address = leg['end_address']
            start_loc = leg['start_location']
            end_loc = leg['end_location']
            s_node = get_node(latitude=start_loc['lat'],
                              longitude=start_loc['lng'])
            # s_node.save()
            e_node = get_node(latitude=end_loc['lat'],
                            longitude=end_loc['lng'])
            # e_node.save()
            steps = leg['steps']
            current_leg = Leg(duration_text=duration_text,
                              duration_value=duration_value,
                              distance_text=distance_text,
                              distance_value=distance_value,
                              start_address=start_address,
                              end_address=end_address,
                              start_location=s_node,
                              end_location=e_node)
            current_leg.save()
            for step in steps:
                html = step['html_instructions']
                distance_text = step['distance']['text']
                distance_value = step['distance']['value']
                duration_text = step['duration']['text']
                duration_value = step['duration']['value']
                start_location = step['start_location']
                end_location = step['end_location']
                start_node = get_node(latitude=start_location['lat'],
                                  longitude=start_location['lng'])
                # start_node.save()
                end_node = get_node(latitude=end_location['lat'],
                                longitude=end_location['lng'])
                # end_node.save()
                current_step = get_step(html,
                                     duration_text,
                                     duration_value,
                                     distance_text,
                                     distance_value,
                                     start_node,
                                     end_node)
                current_leg.steps.add(current_step)
            current_leg.save()
            current_route.legs.add(current_leg)
        current_route.save()
    return all_routes

def get_node(longitude, latitude):
    try:
        node = Node.objects.get(longitude=longitude, latitude=latitude)
    except Node.DoesNotExist:
        node = Node(longitude=longitude, latitude=latitude)
        node.save()
    return node

def get_step(html, duration_text, duration_value,
             distance_text,distance_value, start_node,end_node):
    try:
        current_step = Step.objects.get(start_location = start_node, end_location = end_node)
    except Step.DoesNotExist:
        current_step = Step(html_instructions=html,
                            duration_text=duration_text,
                            duration_value=duration_value,
                            distance_text=distance_text,
                            distance_value=distance_value,
                            start_location=start_node,
                            end_location=end_node)
        current_step.save()
    return current_step
        
#@author: Monayri
#@param myStep: The Step that i am currently at
#@param legID: The id of the leg i am taking
#@param destination: The destination Node
#@return: list of routes
def getalternatives(leg, myStep, destination, location):
    #First i will check if the alternative can be fetched from the database
#    startNode = Node.objects.get(id = location)
#    endNode = Node.objects.get(id = destination)
#    startStep = Step.objects.filter(start_location = location)
#    endStep = Step.objects.filter(end_location = destination)
#    print endNode.longitude
#    legs = Leg.objects.all()
#    routes = []
#    if(startStep != None and endStep!= None):
#        print startStep
#        print endStep
#        for leg in legs :
#            data = leg.steps.all()
#            current_steps = []
#            for cstep in data:
#                current_steps.append(cstep)
#            for step in startStep :
#                for step2 in endStep : 
#                    if step in current_steps:
#                        if step2 in current_steps:
#                            routeSummary = "" # Should Contain the route summary
#                            currentRoute = Route(summary = routeSummary)
#                            currentRoute.save()
#                            current_leg = Leg(duration_text = "", 
#                              duration_value = 1, 
#                              distance_text = "", 
#                              distance_value = 1, 
#                              start_address = "longitude:" + str(startNode.longitude) + "latitude: " + str(startNode.latitude), 
#                              end_address = "longitude:" + str(endNode.longitude) + "latitude: " + str(endNode.latitude))
#                            current_leg.save()
#                            for x in range(current_steps.index(step), current_steps.index(step2)):
#                                current_leg.steps.add(current_steps[x])
#                                current_steps[x].save()
#                            current_leg.save()
#                            currentRoute.legs.add(current_leg)
#                            currentRoute.save()
#                            routes.append(currentRoute)

    #First i will call the subRoutes Method 
    if myStep == None:
        return getdirections(location.latitude+","+location.start_location.longitude, destination.start_location.latitude+","+destination.longitude)
#    routes = compute_subroutes(leg, myStep)
    routes =[]
    if(len(routes)==0):
        return getdirections(myStep.start_location.latitude+","+myStep.start_location.longitude, destination.start_location.latitude+","+destination.longitude)
    if leg != None :
        steps =[] 
        duration = 0
        distance = 0
        for step in leg.steps:
            if(step != myStep):
                steps.append(step)
                duration += step.duration_value
                distance += step.distance_value
            else:
                break
        for route in routes:
            for myleg in route.legs:
                summ =""
                current_route=Route(summary=summ)
                current_route.save()
                distance_text = ""
                distance_value = distance + myleg.distance_value
                duration_text = ""
                duration_value = duration + myleg.duration_value
                start_address = leg.start_address
                end_address = myleg.end_address
                start_loc = leg.start_location
                end_loc = myleg.end_location
                current_leg = Leg(duration_text = duration_text, 
                                  duration_value = duration_value, 
                                  distance_text = distance_text, 
                                  distance_value = distance_value, 
                                  start_address = start_address, 
                                  end_address = end_address,
                                  start_location = start_loc, 
                                  end_location = end_loc)
                current_leg.save()
                current_leg.steps.extend(steps)
                current_leg.steps.extend(leg.steps)
                current_leg.save()
                current_route.legs.add(current_leg)
                current_route.save()
#        response +=  '"routes" :[]'

    
    response = {"routes":[]}
    for route in routes :
        r = [{"summary" : route.summary, "legs":[]}]
        for leg in route.legs:
            start_node = Node.objects.get(leg.start_location.id)
            end_node = Node.objects.get(leg.end_location.id)
            l = [{"distance" : {"text":leg.distance_text, 
                               "value": leg.distance_value}, 
                 "end_address": leg.end_address,
                 "end_location": {"lat" : end_node.latitude ,
                                  "lng" : end_node.longitude},
                 "start_address" : leg.start_address,
                 "start_location" : {"lat" : start_node.latitude,
                                     "lng" : start_node.longitude},
                 "steps" : []
                 }]
            for step in leg.steps:
                start_node2 = Node.objects.get(step.start_location.id)
                end_node2 = Node.objects.get(step.end_location.id)
                s = [{"distance" : {"text": step.distance_text,
                                   "value": step.distance_value},
                     "duration" : {"text": step.duration_text,
                                   "value": step.duration_value},
                     "end_location": {"lat": end_node2.latitude,
                                      "lng": end_node2.longitude},
                     "start_location": {"lat": end_node2.latitude,
                                      "lng": end_node2.longitude}
                     }]
                l["steps"] += s
            r["legs"] +=l
        response["routes"]+=r             
    return response

# Author : Ahmed Abouraya
# takes a JSONObject and updates all steps speeds with the information in the database
def updateResult(result):
        routes = result['routes']
        for route in routes :
                summ = route['summary']
                legs = route['legs']

                for leg in legs :
                        distance_text = leg['distance']['text']
                        distance_value = leg['distance']['value']
                        duration_text = leg['duration']['text']
                        duration_value = leg['duration']['value']
                        start_address = leg['start_address']
                        end_address = leg['end_address']
                        start_loc = leg['start_location']
                        end_loc = leg['end_location']
                        steps = leg['steps']
                        for step in steps:
                                html = step['html_instructions']
                                distance_text = step['distance']['text']
                                distance_value = step['distance']['value']
                                duration_text = step['duration']['text']
                                duration_value = step['duration']['value']
                                current_start_location = step['start_location']
                                current_end_location = step['end_location']
                                stepHistoryList = Step_History.objects.filter(step__start_location__latitude=current_start_location['lat'],
                                                    step__start_location__longitude=current_start_location['lng'],
                                                    step__end_location__latitude=current_end_location['lat'],
                                                    step__end_location__longitude=current_end_location['lng'])[:5]
                                counter=0
                                avgSpeed=0
                                for s in stepHistoryList.all():
                                        counter=counter+1
                                        avgSpeed=avgSpeed+s.speed
                                if counter==0:
                                        step['speed']=-1
                                else:                           
                                        avgSpeed=avgSpeed/counter
                                        step['speed']=avgSpeed
        return result

# calculates distance between two nodes
def getDistance(current,target):
        lat = current['lat'] / 1E6 - target['lat']  / 1E6;
        lng = current['lng']  / 1E6 - target['lng']  / 1E6;
        return math.sqrt(lat*lat+lng*lng)
        
# checks if the current road is blocked,if so it updates the database
# loops over all steps, when the currentStep is reached, checks whether the driver has reached the end of the step or not if yes insert information in database
# checks for future steps if they're blocked if yes checks for alternatives
def evaluate(origin, destination, result, speed, currentStep, startTime):
        routes = result['routes']
        for route in routes :
                summ = route['summary']
                legs = route['legs']

                for leg in legs :
                        distance_text = leg['distance']['text']
                        distance_value = leg['distance']['value']
                        duration_text = leg['duration']['text']
                        duration_value = leg['duration']['value']
                        start_address = leg['start_address']
                        end_address = leg['end_address']
                        start_loc = leg['start_location']
                        end_loc = leg['end_location']
                        steps = leg['steps']

                        flag=True
                        #check if speed is 0 insert current step as blocked
                        if blockedRoad(speed):
                                currentStepHistory = Step_History(step = currentStep,time=datetime.now(),speed=0)
                                currentStepHistory.save()

                        for step in steps:
                                if step==currentStep:
                                #if current step is not reached check if the user has reached it's end
                                        flag=False
                                        if getDistance(origin,currentStep['end_location'])<0.0002 :
                                                currentStepHistory = Step_History(step = currentStep,time=datetime.now(),
                                                                            speed=(startTime-datetime.now())/currentStep['distance']['value'])
                                        currentStepHistory.save()
                                
                                if flag :
                                #if currentStep is not reached skip
                                        continue

                                #if currentStep is reached check if a future step is blocked


				html = step['html_instructions']
				distance_text = step['distance']['text']
				distance_value = step['distance']['value']
				duration_text = step['duration']['text']
				duration_value = step['duration']['value']
				current_start_location = step['start_location']
				current_end_location = step['end_location']
	
				stepHistoryLists=Step_History.objects.filter(step__start_location__latitude=current_start_location['lat'],
				                                        step__start_location__longitude=current_start_location['lng'],
				                                        step__end_location__latitude=current_end_location['lat'],
				                                        step__end_location__longitude=current_end_location['lng'])[:5]
				counter=0
				for s in stepHistoryLists.all():
					if blockedRoad(s.speed):
						counter=counter+1
				if counter>0:
				#request for alternatives
					return updateResult(getalternatives(leg, step, destination, origin))
		return updateResult(result)

# used for testing                       
def test_evaluate(origin, destination,leg,speed,CurrentStep):
        steps = leg.steps
        flag=True
        #check if speed is 0 insert current step as blocked
        if blockedRoad(speed):
                currentStepHistory = Step_History(step = CurrentStep,time=datetime.now(),speed=0)
                currentStepHistory.save()
        #insert current step as blocked
        for curStep in steps.all():
                #if currentStep is not reached skip
                if curStep==CurrentStep:
                        flag=False
                else:
                        continue
                #if currentStep is reached check if a future step is blocked
                
                #html = step['html_instructions']
                #distance_text = step['distance']['text']
                #distance_value = step['distance']['value']
                #duration_text = step['duration']['text']
                #duration_value = step['duration']['value']
                current_start_location = curStep.start_location
                current_end_location = curStep.end_location

                stepHistoryLists=Step_History.objects.filter(step__start_location=current_start_location)[:5]
                counter=0
                for s in stepHistoryLists.all():
                        if blockedRoad(s.speed):
                                counter=counter+1
                if counter>0:
                #request for alternatives
                        #return getalternatives(origin, destination)
                        return True
        return False
        
#determines whether a road is blocked or not
def blockedRoad(speed):
	return speed == 0

# @author:              Shanab
# @param leg:           current leg that the user is moving in (can be None)
# @param step:          current step that the user is moving in
# @param destination:   destination node for the user
# The method tries to find the possible subroutes that can go from
# the end node of the provided step to the end of the provided leg.
# Also the method saves the newly found subroute
# If there wasn't any subroutes found, the method will return None!
def compute_subroutes(leg, step, destination):
    start_node = step.end_location
    end_node = destination
    legs = list(Leg.objects.filter(steps__start_location = start_node).filter(steps__end_location = end_node))
    # If one of the filtered legs happens to be the input leg, then remove it
    try:
        legs.remove(leg)
    except:
        pass
    print "Found " + str(len(legs)) + " leg(s)!"
    if len(legs) != 0:
        return find_and_create_subroute(legs, start_node, end_node)
    else:
        return []
    pass

# @author:              Shanab
# @param legs:          All the legs that have a path that will lead
#                       from start_node to end_node
# @param start_node:    the start node of the subroute
# @param end_node:      the end node of the subroute
# The method finds the subroute that will lead from the provided
# start node to the provided end node in the input leg
def find_and_create_subroute(legs, start_node, end_node):
    result_routes = []
    for leg in legs:
        steps = ordered_steps(leg)
        print "Steps: " + str(steps)
        i = 0
        for step in steps:
            if step.start_location == start_node:
                start_index = i
                break
            i += 1
        for step in steps[start_index:]:
            if step.end_location == end_node:
                end_index = i
                break
            i += 1
        end_index += 1
        print "Start index:\t" + str(start_index)
        print "End index:\t" + str(end_index)
        subroute_steps = steps[start_index:end_index]
        print "Subroute Steps: " + str(subroute_steps)
        if len(subroute_steps) != len(steps):       # if the subroute length was equal to the route length
                                                    # this means the route doesn't need to be saved
            new_leg =   Leg(duration_value  = sum_duration_values(subroute_steps),
                            distance_value  = sum_distance_values(subroute_steps),
                            start_location  = start_node,
                            end_location    = end_node)
            new_leg.save()                
            new_leg.steps = subroute_steps
            new_leg.save()
            new_route = Route()
            new_route.save()
            new_route.legs.add(new_leg)
            new_route.save()
            result_routes.append(new_route)
        else:
            route = leg.route_set.all()[0]
            result_routes.append(route)
    return result_routes

# @author:  Shanab
# @param:   x
# @param:   y
# returns the addition of two numbers x and y
def add(x,y): return x + y

# @author:  Shanab
# @param    step
# returns the distance value of the provided step
def get_distance_value(step): return step.distance_value

# @author:  Shanab
# @param    step
# returns the duration value of the provided step
def get_duration_value(step): return step.duration_value

# @author:      Shanab
# @param steps: a list of steps
# returns the summation of distance values for the provided list of steps
def sum_distance_values(steps):
    return reduce(add, map(get_distance_value, steps))

# @author:      Shanab
# @param steps: a list of steps
# returns the summation of duration values for the provided list of steps
def sum_duration_values(steps):
    return reduce(add, map(get_duration_value, steps))

# @author:      Shanab
# @param leg
# returns an ordered list of steps where the end node of a step
# is the start node of the next step
def ordered_steps(leg):
    result = []
    steps = list(leg.steps.all())
    node = leg.start_location
    end_node = leg.end_location
    while True:
        temp_step = [step for step in steps if step.start_location == node][0]
        result.append(temp_step)
        node = temp_step.end_location
        if node == end_node:
            break
    return result
