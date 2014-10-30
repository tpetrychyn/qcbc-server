import urllib2
import threading
import time
import traceback
import json
from jinja2 import Template
import cPickle as pickle
import sqlite3
import time
import haversine
import os

class TransitLive:

    API = {
        'MAIN': 'http://transitlive.com/%s',
        #'BUS_INFO': ['ajax/livemap.php?action=dev_bus&a=0&low=0', 'busID'],
        'BUS_INFO': ['json/buses.js', 'busID'],
        'ROUTE_INFO': ['ajax/livemap.php?action=get_routes', 'routeID'],
        'STOP_TIMES': 'ajax/livemap.php?action=stop_times&stop=%s&routes=%s&lim=%s',
        'DETOURS': 'ajax/livemap.php?action=detours',
        'ROUTE_PATHS': "json/polyLines/route%s.js",
        'STOPS': "json/stops.js",
        'STOP_INFO': 'testlines/route%s.js'
    }
    
    template_locations_all = Template(open("templates/template_buslocation_all.xml").read())
    template_stoptimes = Template(open("templates/template_stoptimes.xml").read())
    template_detours = Template(open("templates/template_detours.xml").read())
    template_stops = Template(open("templates/template_stops.xml").read())
    template_route = Template(open("templates/template_route.xml").read())
    template_location = Template(open("templates/template_buslocation.xml").read())

    bus_json = '[{"bus_id":"619","latitude":"50.46448667","longitude":"-104.61821500","bearing":"179","route_id":"40","low_floor":"0","line_name":"ALBERT SOUTH"},{"bus_id":"619","latitude":"50.46448667","longitude":"-104.61821500","bearing":"179","route_id":"40","low_floor":"0","line_name":"ALBERT NORTH"},{"bus_id":"623","latitude":"50.49780167","longitude":"-104.64537167","bearing":"357","route_id":"40","low_floor":"0","line_name":"ALBERT SOUTH"},{"bus_id":"623","latitude":"50.49780167","longitude":"-104.64537167","bearing":"357","route_id":"40","low_floor":"0","line_name":"ALBERT NORTH"},{"bus_id":"655","latitude":"50.45828500","longitude":"-104.62856167","bearing":"271","route_id":"4","low_floor":"0","line_name":"HILLSDALE"},{"bus_id":"655","latitude":"50.45828500","longitude":"-104.62856167","bearing":"271","route_id":"4","low_floor":"0","line_name":"WALSH ACRES"},{"bus_id":"544","latitude":"50.43240167","longitude":"-104.53726333","bearing":"357","route_id":"12","low_floor":"0","line_name":"VARSITY PARK"},{"bus_id":"544","latitude":"50.43240167","longitude":"-104.53726333","bearing":"357","route_id":"12","low_floor":"0","line_name":"MOUNT ROYAL"},{"bus_id":"659","latitude":"50.46136000","longitude":"-104.55349333","bearing":"75","route_id":"9","low_floor":"0","line_name":"PARKRIDGE"},{"bus_id":"659","latitude":"50.46136000","longitude":"-104.55349333","bearing":"75","route_id":"9","low_floor":"0","line_name":"ALBERT PARK"},{"bus_id":"601","latitude":"50.45011500","longitude":"-104.61521833","bearing":"179","route_id":"4","low_floor":"0","line_name":"HILLSDALE"},{"bus_id":"601","latitude":"50.45011500","longitude":"-104.61521833","bearing":"179","route_id":"4","low_floor":"0","line_name":"WALSH ACRES"},{"bus_id":"651","latitude":"50.47694167","longitude":"-104.65125667","bearing":"86","route_id":"3","low_floor":"0","line_name":"UNIVERSITY"},{"bus_id":"651","latitude":"50.47694167","longitude":"-104.65125667","bearing":"86","route_id":"3","low_floor":"0","line_name":"SHERWOOD"},{"bus_id":"587","latitude":"50.45040833","longitude":"-104.61690667","bearing":"275","route_id":"1","low_floor":"0","line_name":"DIEPPE"},{"bus_id":"587","latitude":"50.45040833","longitude":"-104.61690667","bearing":"275","route_id":"1","low_floor":"0","line_name":"BROAD NORTH"},{"bus_id":"621","latitude":"50.45148667","longitude":"-104.60632000","bearing":"4","route_id":"1","low_floor":"0","line_name":"DIEPPE"},{"bus_id":"621","latitude":"50.45148667","longitude":"-104.60632000","bearing":"4","route_id":"1","low_floor":"0","line_name":"BROAD NORTH"},{"bus_id":"652","latitude":"50.46498000","longitude":"-104.56223500","bearing":"274","route_id":"8","low_floor":"0","line_name":"NOR.HEIGHTS"},{"bus_id":"652","latitude":"50.46498000","longitude":"-104.56223500","bearing":"274","route_id":"8","low_floor":"0","line_name":"EASTVIEW"},{"bus_id":"622","latitude":"50.45036500","longitude":"-104.60716667","bearing":"270","route_id":"10","low_floor":"0","line_name":"NORMANVIEW"},{"bus_id":"622","latitude":"50.45036500","longitude":"-104.60716667","bearing":"270","route_id":"10","low_floor":"0","line_name":"RCMP"},{"bus_id":"610","latitude":"50.40466167","longitude":"-104.62150333","bearing":"96","route_id":"8","low_floor":"0","line_name":"NOR.HEIGHTS"},{"bus_id":"610","latitude":"50.40466167","longitude":"-104.62150333","bearing":"96","route_id":"8","low_floor":"0","line_name":"EASTVIEW"},{"bus_id":"627","latitude":"50.45581167","longitude":"-104.68684167","bearing":"359","route_id":"1","low_floor":"0","line_name":"DIEPPE"},{"bus_id":"627","latitude":"50.45581167","longitude":"-104.68684167","bearing":"359","route_id":"1","low_floor":"0","line_name":"BROAD NORTH"},{"bus_id":"809","latitude":"50.45042500","longitude":"-104.60911333","bearing":"292","route_id":"9","low_floor":"0","line_name":"PARKRIDGE"},{"bus_id":"809","latitude":"50.45042500","longitude":"-104.60911333","bearing":"292","route_id":"9","low_floor":"0","line_name":"ALBERT PARK"},{"bus_id":"606","latitude":"50.44720000","longitude":"-104.57274500","bearing":"277","route_id":"7","low_floor":"0","line_name":"GLENCAIRN"},{"bus_id":"606","latitude":"50.44720000","longitude":"-104.57274500","bearing":"277","route_id":"7","low_floor":"0","line_name":"WHIT. PARK"},{"bus_id":"640","latitude":"50.41622833","longitude":"-104.59221833","bearing":"354","route_id":"4","low_floor":"0","line_name":"HILLSDALE"},{"bus_id":"640","latitude":"50.41622833","longitude":"-104.59221833","bearing":"354","route_id":"4","low_floor":"0","line_name":"WALSH ACRES"},{"bus_id":"628","latitude":"50.45045167","longitude":"-104.61241500","bearing":"272","route_id":"2","low_floor":"0","line_name":"WOOD. GROVE"},{"bus_id":"628","latitude":"50.45045167","longitude":"-104.61241500","bearing":"272","route_id":"2","low_floor":"0","line_name":"ARGYLE PARK"},{"bus_id":"609","latitude":"50.45030833","longitude":"-104.60691500","bearing":"92","route_id":"8","low_floor":"0","line_name":"NOR.HEIGHTS"},{"bus_id":"609","latitude":"50.45030833","longitude":"-104.60691500","bearing":"92","route_id":"8","low_floor":"0","line_name":"EASTVIEW"},{"bus_id":"639","latitude":"50.44876000","longitude":"-104.60656000","bearing":"178","route_id":"2","low_floor":"0","line_name":"WOOD. GROVE"},{"bus_id":"639","latitude":"50.44876000","longitude":"-104.60656000","bearing":"178","route_id":"2","low_floor":"0","line_name":"ARGYLE PARK"},{"bus_id":"630","latitude":"50.40772000","longitude":"-104.64533500","bearing":"113","route_id":"40","low_floor":"0","line_name":"ALBERT SOUTH"},{"bus_id":"630","latitude":"50.40772000","longitude":"-104.64533500","bearing":"113","route_id":"40","low_floor":"0","line_name":"ALBERT NORTH"},{"bus_id":"611","latitude":"50.40543000","longitude":"-104.63855500","bearing":"89","route_id":"7","low_floor":"0","line_name":"GLENCAIRN"},{"bus_id":"611","latitude":"50.40543000","longitude":"-104.63855500","bearing":"89","route_id":"7","low_floor":"0","line_name":"WHIT. PARK"},{"bus_id":"662","latitude":"50.48136167","longitude":"-104.66407833","bearing":"180","route_id":"4","low_floor":"0","line_name":"HILLSDALE"},{"bus_id":"662","latitude":"50.48136167","longitude":"-104.66407833","bearing":"180","route_id":"4","low_floor":"0","line_name":"WALSH ACRES"}]'
    route_json = '[{"route_id":"1","name":"DIEPPE - BROAD NORTH","colour":"#8FCEC3","stop_days":"WSU","disabled":"0"},{"route_id":"2","name":"WOOD. GROVE - ARGYLE PARK","colour":"#EC5643","stop_days":"WSU","disabled":"0"},{"route_id":"3","name":"UNIVERSITY - SHERWOOD","colour":"#F2AE4F","stop_days":"WSU","disabled":"0"},{"route_id":"4","name":"HILLSDALE - WALSH ACRES","colour":"#F2AE4F","stop_days":"WSU","disabled":"0"},{"route_id":"5","name":"UPLANDS - DOWNTOWN","colour":"#2E3092","stop_days":"WS","disabled":"0"},{"route_id":"6","name":"ROSS INDUST. - WESTHILL","colour":"#204D31","stop_days":"WS","disabled":"0"},{"route_id":"7","name":"GLENCAIRN - WHIT. PARK","colour":"#668BC7","stop_days":"WSU","disabled":"0"},{"route_id":"8","name":"NOR.HEIGHTS - EASTVIEW","colour":"#A42C31","stop_days":"WSU","disabled":"0"},{"route_id":"9","name":"PARKRIDGE - ALBERT PARK","colour":"#668BC7","stop_days":"WSU","disabled":"0"},{"route_id":"10","name":"NORMANVIEW - RCMP","colour":"#E93D93","stop_days":"WSU","disabled":"0"},{"route_id":"12","name":"VARSITY PARK - MOUNT ROYAL","colour":"#00A54F","stop_days":"WSU","disabled":"0"},{"route_id":"14","name":"WINDSOR PK - SPRUCE MED","colour":"#8FCEC3","stop_days":"W","disabled":"0"},{"route_id":"15","name":"HERITAGE","colour":"#D80961","stop_days":"WS","disabled":"0"},{"route_id":"16","name":"LAKERIDGE","colour":"#57585A","stop_days":"W","disabled":"0"},{"route_id":"17","name":"MAPLERIDGE","colour":"#AF62A8","stop_days":"WS","disabled":"0"},{"route_id":"18","name":"UNIVERSITY - HARBOUR LAND","colour":"#CADB2A","stop_days":"W","disabled":"0"},{"route_id":"21","name":"UNIVERSITY - GLENCAIRN","colour":"#E6DA17","stop_days":"W","disabled":"0"},{"route_id":"30","name":"UNIVERSITY - ROCHDALE","colour":"#57585A","stop_days":"W","disabled":"0"},{"route_id":"40","name":"ALBERT SOUTH - ALBERT NORTH","colour":"#00AEEF","stop_days":"W","disabled":"0"},{"route_id":"50","name":"VICTORIA E - VICTORIA W","colour":"#522626","stop_days":"W","disabled":"0"}]'
    route6_json = '{    "type": "FeatureCollection",    "features": [ { "geometry": {  "style": {  "color": "#204D31",  "opacity": "1"  },  "type": "LineString",  "coordinates": [  [   -104.70896999999999,   50.481059999999999  ],  [   -104.70585,   50.481070000000003  ],  [   -104.70295,   50.481099999999998  ],  [   -104.69722,   50.481769999999997  ],  [   -104.69663,   50.481729999999999  ],  [   -104.69043000000001,   50.480930000000001  ],  [   -104.68778,   50.480910000000002  ],  [   -104.68747,   50.480960000000003  ],  [   -104.68369,   50.481020000000001  ],  [   -104.67845,   50.479939999999999  ],  [   -104.67189,   50.479979999999998  ],  [   -104.67116,   50.479959999999998  ],  [   -104.67068999999999,   50.47992  ],  [   -104.67039,   50.479849999999999  ],  [   -104.66997000000001,   50.479700000000001  ],  [   -104.66909,   50.479190000000003  ],  [   -104.66661999999999,   50.480780000000003  ],  [   -104.66616,   50.480890000000002  ],  [   -104.6626,   50.480899999999998  ],  [   -104.65255999999999,   50.480919999999998  ],  [   -104.65252,   50.47701  ],  [   -104.65031,   50.476999999999997  ],  [   -104.64954,   50.476930000000003  ],  [   -104.64852999999999,   50.476739999999999  ],  [   -104.64818,   50.477530000000002  ],  [   -104.64704,   50.478720000000003  ],  [   -104.64554,   50.479640000000003  ],  [   -104.64525,   50.479819999999997  ],  [   -104.64375,   50.48039  ],  [   -104.64268,   50.480609999999999  ],  [   -104.64188,   50.480640000000001  ],  [   -104.64115,   50.480620000000002  ],  [   -104.63263999999999,   50.480609999999999  ],  [   -104.63263999999999,   50.479309999999998  ],  [   -104.62350000000001,   50.479300000000002  ],  [   -104.62273,   50.479300000000002  ],  [   -104.62227,   50.479190000000003  ],  [   -104.62134,   50.478969999999997  ],  [   -104.62085999999999,   50.478839999999998  ],  [   -104.62026,   50.478830000000002  ],  [   -104.61796,   50.478870000000001  ],  [   -104.61796,   50.48068  ],  [   -104.61226000000001,   50.480690000000003  ],  [   -104.61226000000001,   50.478859999999997  ],  [   -104.59518,   50.478870000000001  ],  [   -104.59517,   50.480730000000001  ],  [   -104.59501,   50.481099999999998  ],  [   -104.59497,   50.481349999999999  ],  [   -104.59464,   50.482300000000002  ],  [   -104.59429,   50.483110000000003  ],  [   -104.59376,   50.484290000000001  ],  [   -104.58253000000001,   50.484290000000001  ],  [   -104.5823,   50.484270000000002  ],  [   -104.58199999999999,   50.484169999999999  ],  [   -104.57992,   50.482869999999998  ],  [   -104.57953000000001,   50.482709999999997  ],  [   -104.57881,   50.482579999999999  ],  [   -104.57186,   50.481470000000002  ],  [   -104.57787,   50.475999999999999  ],  [   -104.57525,   50.474490000000003  ],  [   -104.571,   50.478409999999997  ],  [   -104.5706,   50.479529999999997  ],  [   -104.57252,   50.47992  ],  [   -104.57313000000001,   50.480220000000003  ],  [   -104.57171,   50.481529999999999  ],  [   -104.57877999999999,   50.482610000000001  ],  [   -104.57951,   50.482770000000002  ],  [   -104.57989999999999,   50.482939999999999  ],  [   -104.58201,   50.48424  ],  [   -104.58229,   50.484340000000003  ],  [   -104.58255,   50.484349999999999  ],  [   -104.59394,   50.484340000000003  ],  [   -104.59446,   50.483130000000003  ],  [   -104.59482,   50.482329999999997  ],  [   -104.5951,   50.481580000000001  ],  [   -104.59520000000001,   50.481160000000003  ],  [   -104.59522,   50.480580000000003  ],  [   -104.59523,   50.478920000000002  ],  [   -104.61219,   50.478909999999999  ],  [   -104.61218,   50.480730000000001  ],  [   -104.61828,   50.480739999999997  ],  [   -104.6183,   50.478920000000002  ],  [   -104.62027999999999,   50.478900000000003  ],  [   -104.62085999999999,   50.478909999999999  ],  [   -104.62144000000001,   50.479050000000001  ],  [   -104.6223,   50.47927  ],  [   -104.62287999999999,   50.47936  ],  [   -104.62365,   50.479349999999997  ],  [   -104.63256,   50.47936  ],  [   -104.63257,   50.480640000000001  ],  [   -104.64127999999999,   50.480670000000003  ],  [   -104.64201,   50.48068  ],  [   -104.64257000000001,   50.48066  ],  [   -104.64385,   50.480409999999999  ],  [   -104.64518,   50.479900000000001  ],  [   -104.64567,   50.479660000000003  ],  [   -104.64715,   50.47871  ],  [   -104.64829,   50.477510000000002  ],  [   -104.64861000000001,   50.476799999999997  ],  [   -104.64967,   50.476990000000001  ],  [   -104.65044,   50.477060000000002  ],  [   -104.65241,   50.477040000000002  ],  [   -104.65251000000001,   50.480989999999998  ],  [   -104.66627,   50.480930000000001  ],  [   -104.66674999999999,   50.48077  ],  [   -104.66909,   50.47925  ],  [   -104.67007,   50.479770000000002  ],  [   -104.67058,   50.479959999999998  ],  [   -104.67131000000001,   50.48001  ],  [   -104.67829999999999,   50.479970000000002  ],  [   -104.68371999999999,   50.481059999999999  ],  [   -104.68733,   50.481000000000002  ],  [   -104.68798,   50.481059999999999  ],  [   -104.69038999999999,   50.481059999999999  ],  [   -104.69656999999999,   50.481789999999997  ],  [   -104.69732999999999,   50.4818  ],  [   -104.70312,   50.481140000000003  ],  [   -104.70594,   50.481099999999998  ],  [   -104.70583999999999,   50.482030000000002  ],  [   -104.70889,   50.482030000000002  ],  [   -104.70896999999999,   50.481000000000002  ]  ] }, "type": "Feature", "properties": {  "days": "W",  "id": 6,  "name": "6: ROSS INDUST. - WESTHILL" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.618078",  "50.479389"  ] }, "type": "Feature", "properties": {  "id": "0059",  "dir": "NB",  "name": "ALBERT ST @ 6TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.615632",  "50.480691"  ] }, "type": "Feature", "properties": {  "id": "0060",  "dir": "EB",  "name": "7TH AVE N @ SMITH ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.615605",  "50.480718"  ] }, "type": "Feature", "properties": {  "id": "0088",  "dir": "WB",  "name": "7TH AVE N @ SMITH ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.595767",  "50.478893"  ] }, "type": "Feature", "properties": {  "id": "0096",  "dir": "WB",  "name": "6TH AVE N @ WINNIPEG ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.618395",  "50.478876"  ] }, "type": "Feature", "properties": {  "id": "0193",  "dir": "WB",  "name": "6TH AVE N @ ALBERT ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.652547",  "50.480695"  ] }, "type": "Feature", "properties": {  "id": "0215",  "dir": "SB",  "name": "MCINTOSH ST @ 7TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.652213",  "50.477000"  ] }, "type": "Feature", "properties": {  "id": "0216",  "dir": "EB",  "name": "SHERWOOD DR @ MCINTOSH ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.648773",  "50.476781"  ] }, "type": "Feature", "properties": {  "id": "0425",  "dir": "WB",  "name": "SHERWOOD DR @ STAPLEFORD CR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.652503",  "50.477230"  ] }, "type": "Feature", "properties": {  "id": "0426",  "dir": "NB",  "name": "MCINTOSH ST @ SHERWOOD DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.652491",  "50.479155"  ] }, "type": "Feature", "properties": {  "id": "0427",  "dir": "NB",  "name": "MCINTOSH ST @ ALCOVE PL" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.706206",  "50.481156"  ] }, "type": "Feature", "properties": {  "id": "0443",  "dir": "WB",  "name": "SHERWOOD DR @ HERMAN CRESCENT" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.701039",  "50.481315"  ] }, "type": "Feature", "properties": {  "id": "0444",  "dir": "EB",  "name": "SHERWOOD DR @ FAIRWAY RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.697849",  "50.481684"  ] }, "type": "Feature", "properties": {  "id": "0445",  "dir": "EB",  "name": "SHERWOOD DR @ WARWICK DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.695279",  "50.481603"  ] }, "type": "Feature", "properties": {  "id": "0446",  "dir": "EB",  "name": "SHERWOOD DR @ DOIRON RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.690221",  "50.480955"  ] }, "type": "Feature", "properties": {  "id": "0447",  "dir": "EB",  "name": "SHERWOOD DR @ VENTURE RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.684723",  "50.480958"  ] }, "type": "Feature", "properties": {  "id": "0448",  "dir": "EB",  "name": "SHERWOOD DR @ GOLDIE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.681711",  "50.480592"  ] }, "type": "Feature", "properties": {  "id": "0449",  "dir": "EB",  "name": "SHERWOOD DR @ DOROTHY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.668848",  "50.479324"  ] }, "type": "Feature", "properties": {  "id": "0458",  "dir": "NB",  "name": "7TH AVE N @ SHERWOOD DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.664732",  "50.480874"  ] }, "type": "Feature", "properties": {  "id": "0459",  "dir": "EB",  "name": "7TH AVE N @ MCCARTHY BLVD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.658985",  "50.480876"  ] }, "type": "Feature", "properties": {  "id": "0460",  "dir": "EB",  "name": "7TH AVE N @ CHAMP CR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.655904",  "50.480877"  ] }, "type": "Feature", "properties": {  "id": "0461",  "dir": "EB",  "name": "7TH AVE N @ MILNE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.648469",  "50.476882"  ] }, "type": "Feature", "properties": {  "id": "0462",  "dir": "NB",  "name": "STAPLEFORD CR @ SHERWOOD DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.646191",  "50.479239"  ] }, "type": "Feature", "properties": {  "id": "0463",  "dir": "NB",  "name": "STAPLEFORD CR @ EDDY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.643387",  "50.480440"  ] }, "type": "Feature", "properties": {  "id": "0464",  "dir": "EB",  "name": "STAPLEFORD CR @ DROPE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.640831",  "50.480606"  ] }, "type": "Feature", "properties": {  "id": "0465",  "dir": "EB",  "name": "DONAHUE AVE @ PASQUA ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.637074",  "50.480616"  ] }, "type": "Feature", "properties": {  "id": "0466",  "dir": "EB",  "name": "DONAHUE AVE @ DERBY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.632639",  "50.480442"  ] }, "type": "Feature", "properties": {  "id": "0467",  "dir": "SB",  "name": "ARGYLE ST N @ DONAHUE AVE" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.632266",  "50.479278"  ] }, "type": "Feature", "properties": {  "id": "0468",  "dir": "EB",  "name": "6TH AVE N @ ARGYLE ST N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.629475",  "50.479471"  ] }, "type": "Feature", "properties": {  "id": "0487",  "dir": "WB",  "name": "6TH AVE N @ GARNET ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.632583",  "50.479590"  ] }, "type": "Feature", "properties": {  "id": "0488",  "dir": "NB",  "name": "ARGYLE ST N @ 6TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.632998",  "50.480653"  ] }, "type": "Feature", "properties": {  "id": "0489",  "dir": "WB",  "name": "DONAHUE AVE @ ARGYLE ST N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.637571",  "50.480652"  ] }, "type": "Feature", "properties": {  "id": "0490",  "dir": "WB",  "name": "DONAHUE AVE @ DERBY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.641453",  "50.480642"  ] }, "type": "Feature", "properties": {  "id": "0491",  "dir": "WB",  "name": "STAPLEFORD CR @ PASQUA ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.643995",  "50.480293"  ] }, "type": "Feature", "properties": {  "id": "0492",  "dir": "WB",  "name": "STAPLEFORD CR @ DROPE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.646564",  "50.479046"  ] }, "type": "Feature", "properties": {  "id": "0493",  "dir": "WB",  "name": "STAPLEFORD CR @ EDDY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.652796",  "50.480906"  ] }, "type": "Feature", "properties": {  "id": "0494",  "dir": "WB",  "name": "7TH AVE N @ MCINTOSH ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.657811",  "50.480904"  ] }, "type": "Feature", "properties": {  "id": "0495",  "dir": "WB",  "name": "7TH AVE N @ PICKARD ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.661610",  "50.480903"  ] }, "type": "Feature", "properties": {  "id": "0496",  "dir": "WB",  "name": "7TH AVE N @ HANLEY CR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.665174",  "50.480902"  ] }, "type": "Feature", "properties": {  "id": "0497",  "dir": "WB",  "name": "7TH AVE N @ MCCARTHY BLVD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.681435",  "50.480574"  ] }, "type": "Feature", "properties": {  "id": "0507",  "dir": "WB",  "name": "SHERWOOD DR @ DOROTHY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.685248",  "50.480985"  ] }, "type": "Feature", "properties": {  "id": "0508",  "dir": "WB",  "name": "SHERWOOD DR @ GOLDIE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.688301",  "50.480983"  ] }, "type": "Feature", "properties": {  "id": "0509",  "dir": "WB",  "name": "SHERWOOD DR @ COURTNEY ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.690788",  "50.481055"  ] }, "type": "Feature", "properties": {  "id": "0510",  "dir": "WB",  "name": "SHERWOOD DR @ DISCOVERY RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.695914",  "50.481685"  ] }, "type": "Feature", "properties": {  "id": "0511",  "dir": "WB",  "name": "SHERWOOD DR @ DOIRON RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.701537",  "50.481278"  ] }, "type": "Feature", "properties": {  "id": "0512",  "dir": "WB",  "name": "SHERWOOD DR @ FAIRWAY RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.669276",  "50.479360"  ] }, "type": "Feature", "properties": {  "id": "0862",  "dir": "WB",  "name": "SHERWOOD DR @ 7TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.672509",  "50.480028"  ] }, "type": "Feature", "properties": {  "id": "0863",  "dir": "WB",  "name": "SHERWOOD DR @ HASTINGS CRES" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.674982",  "50.480036"  ] }, "type": "Feature", "properties": {  "id": "0864",  "dir": "WB",  "name": "SHERWOOD DR @ HASTINGS CRES" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.677566",  "50.480026"  ] }, "type": "Feature", "properties": {  "id": "0865",  "dir": "WB",  "name": "SHERWOOD DR @ WILLISTON DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.677538",  "50.479861"  ] }, "type": "Feature", "properties": {  "id": "1159",  "dir": "EB",  "name": "SHERWOOD DR @ MURPHY CRES" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.675148",  "50.479871"  ] }, "type": "Feature", "properties": {  "id": "1160",  "dir": "EB",  "name": "SHERWOOD DR @ HASTINGS CRES" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.672261",  "50.479863"  ] }, "type": "Feature", "properties": {  "id": "1161",  "dir": "EB",  "name": "SHERWOOD DR @ AULD BAY" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.574342",  "50.475203"  ] }, "type": "Feature", "properties": {  "id": "1166",  "dir": "NB",  "name": "LEONARD ST @ HENDERSON DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.655807",  "50.480905"  ] }, "type": "Feature", "properties": {  "id": "1268",  "dir": "WB",  "name": "7TH AVE N @ MILNE ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.570941",  "50.479667"  ] }, "type": "Feature", "properties": {  "id": "1279",  "dir": "WB",  "name": "HENDERSON DR @ LEONARD ST" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.574975",  "50.478769"  ] }, "type": "Feature", "properties": {  "id": "1280",  "dir": "SB",  "name": "MCDONALD ST @ HENDERSON DR" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.577104",  "50.476845"  ] }, "type": "Feature", "properties": {  "id": "1281",  "dir": "SB",  "name": "MCDONALD ST @ HODSMAN RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.708306",  "50.480981"  ] }, "type": "Feature", "properties": {  "id": "1421",  "dir": "EB",  "name": "SHERWOOD DR @ SHILLINGTON ROAD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.595380",  "50.479085"  ] }, "type": "Feature", "properties": {  "id": "1434",  "dir": "SB",  "name": "WINNIPEG ST @ 6TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.621973",  "50.478940"  ] }, "type": "Feature", "properties": {  "id": "1454",  "dir": "EB",  "name": "6TH AVE N @ ANGUS RD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.623272",  "50.479416"  ] }, "type": "Feature", "properties": {  "id": "1455",  "dir": "WB",  "name": "6TH AVE. N @ SHEPHERD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.614762",  "50.478756"  ] }, "type": "Feature", "properties": {  "id": "1456",  "dir": "EB",  "name": "6TH AVE N @ SMITH" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.611958",  "50.478775"  ] }, "type": "Feature", "properties": {  "id": "1457",  "dir": "EB",  "name": "6TH AVE N @ CORNWALL" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.609098",  "50.478793"  ] }, "type": "Feature", "properties": {  "id": "1458",  "dir": "EB",  "name": "6TH AVE N @ HAMILTON" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.606142",  "50.478775"  ] }, "type": "Feature", "properties": {  "id": "1459",  "dir": "EB",  "name": "6TH AVE N @ BROAD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.603240",  "50.478802"  ] }, "type": "Feature", "properties": {  "id": "1460",  "dir": "EB",  "name": "6TH AVE N @ HALIFAX" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.600353",  "50.478747"  ] }, "type": "Feature", "properties": {  "id": "1461",  "dir": "EB",  "name": "6TH AVE N @ OTTOWA" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.597493",  "50.478774"  ] }, "type": "Feature", "properties": {  "id": "1462",  "dir": "EB",  "name": "6TH AVE N @ MONTREAL" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.595034",  "50.479204"  ] }, "type": "Feature", "properties": {  "id": "1463",  "dir": "NB",  "name": "WINNIPEG @ 6TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.584519",  "50.484107"  ] }, "type": "Feature", "properties": {  "id": "1464",  "dir": "EB",  "name": "9TH AVE N @ 297 9TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.581645",  "50.483731"  ] }, "type": "Feature", "properties": {  "id": "1465",  "dir": "EB",  "name": "9TH AVE N @ 119 9TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.578537",  "50.482364"  ] }, "type": "Feature", "properties": {  "id": "1466",  "dir": "EB",  "name": "9TH AVE N @ COOP REFINERY" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.579159",  "50.482795"  ] }, "type": "Feature", "properties": {  "id": "1467",  "dir": "WB",  "name": "9TH AVE N @ COOP REFINERY" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.581479",  "50.484015"  ] }, "type": "Feature", "properties": {  "id": "1468",  "dir": "WB",  "name": "9TH AVE N @ 119 9TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.584712",  "50.484456"  ] }, "type": "Feature", "properties": {  "id": "1469",  "dir": "WB",  "name": "9TH AVE N @ 297 9TH AVE N" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.599400",  "50.479003"  ] }, "type": "Feature", "properties": {  "id": "1470",  "dir": "WB",  "name": "6TH AVE N @ TORONTO" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.603724",  "50.479077"  ] }, "type": "Feature", "properties": {  "id": "1471",  "dir": "WB",  "name": "6TH AVE N @ HALIFAX" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.606791",  "50.478995"  ] }, "type": "Feature", "properties": {  "id": "1472",  "dir": "WB",  "name": "6TH AVE N @ BROAD" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.609609",  "50.479022"  ] }, "type": "Feature", "properties": {  "id": "1473",  "dir": "WB",  "name": "6TH AVE N @ HAMILTON" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.612441",  "50.479050"  ] }, "type": "Feature", "properties": {  "id": "1474",  "dir": "WB",  "name": "6TH AVE N @ CORNWALL" } }, { "geometry": {  "type": "Point",  "coordinates": [  "-104.626505",  "50.479196"  ] }, "type": "Feature", "properties": {  "id": "1536",  "dir": "EB",  "name": "6TH AVE N @ GARNET ST" } }    ]}'
    stoptimes_json = '[{"pred_time":"11:15 PM","intersection":"11TH AVE @ HAMILTON ST","bus_id":null,"stop_id":"1544","route_id":"10","stop_time_id":"2754","line_name":"NORMANVIEW"},{"pred_time":"11:15 PM","intersection":"11TH AVE @ HAMILTON ST","bus_id":"614","stop_id":"1544","route_id":"12","stop_time_id":"34409","line_name":"VARSITY PARK"},{"pred_time":"12:15 AM","intersection":"11TH AVE @ HAMILTON ST","bus_id":"594","stop_id":"1544","route_id":"12","stop_time_id":"44883","line_name":"VARSITY PARK"},{"pred_time":"12:15 AM","intersection":"11TH AVE @ HAMILTON ST","bus_id":"652","stop_id":"1544","route_id":"10","stop_time_id":"7477","line_name":"NORMANVIEW"}]'
    detours_json = '[{"stop_id":"0038","message":"Stop is out of service.  Please use stops on 11th Ave"},{"stop_id":"1497","message":"Stop is out of service"},{"stop_id":"0239","message":"Stop is temporarily out of service."},{"stop_id":"0460","message":"Stop is temporarily out of service"},{"stop_id":"0158","message":"Stop is temporarily out of service - Use Sangster stops"},{"stop_id":"0152","message":"Stop is temporarily out of service"},{"stop_id":"0200","message":"Stop is temporarily out of service"},{"stop_id":"0020","message":"Stop is temporarily out of service, use McMurchy stops"},{"stop_id":"0495","message":"Stop is temporarily out of service"},{"stop_id":"0496","message":"Stop is temporarily out of service"},{"stop_id":"0159","message":"Stop is temporarily out of service - Use McMurchy stop"},{"stop_id":"1499","message":"Stop is out of service"},{"stop_id":"0037","message":"Stop is temporarily out of service"},{"stop_id":"1181","message":"Stop is temporarily out of service"},{"stop_id":"1498","message":"Stop is out of service"},{"stop_id":"1268","message":"Stop is temporarily out of service"}]'
    
    def __init__(self, debug=False):

        print "Initializing TransitLive module"

        self.database = sqlite3.connect(TransitLiveUpdater.DATABASE, check_same_thread=False)

        self.bus_locations = {} # dictionary (bus_id as index)
        self.routes = {} # dictionary (route_id as index)
        self.detours = []

        self.debug = debug
            
        self.route_cache_thread = TransitLiveUpdater.RepeatedUpdater(
            [self.load_route_cache], 1000)
            
        self.route_cache_thread.start()
      
        
    
    def process(self, function, params):
        #print "proc", self.bus_locations[611].latitude
        output = {'error': None, 'response': None}
        
        if function == 'get_bus_location':
            output['response'] = self.request_bus_location(params.get('bus_id'), int(params.get('ts', 0)))

        elif function == 'get_bus_locations':
            output['response'] = self.request_bus_locations(int(params.get('ts', 0)))
            
        elif function == 'get_route':
            output['response'] = self.request_route(params['route_id'])
            
        elif function == 'get_fake':
            import random

            output['response'] = """<buslocations><buslocation><bus_id>640</bus_id>  <route_id>4</route_id>  <longitude>-104.59221833</longitude>  <latitude>50.41622833</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>651</bus_id>  <route_id>3</route_id>  <longitude>-104.65125667</longitude>  <latitude>50.47694167</latitude>  <bearing>0</bearing>  <desc>SHERWOOD</desc></buslocation><buslocation>  <bus_id>652</bus_id>  <route_id>8</route_id>  <longitude>-104.562235</longitude>  <latitude>50.46498</latitude>  <bearing>0</bearing>  <desc>EASTVIEW</desc></buslocation><buslocation>  <bus_id>655</bus_id>  <route_id>4</route_id>  <longitude>-104.62856167</longitude>  <latitude>50.458285</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>659</bus_id>  <route_id>9</route_id>  <longitude>-104.55349333</longitude>  <latitude>50.46136</latitude>  <bearing>0</bearing>  <desc>ALBERT PARK</desc></buslocation><buslocation>  <bus_id>662</bus_id>  <route_id>4</route_id>  <longitude>-104.66407833</longitude>  <latitude>50.48136167</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>544</bus_id>  <route_id>12</route_id>  <longitude>-104.53726333</longitude>  <latitude>50.43240167</latitude>  <bearing>0</bearing>  <desc>MOUNT ROYAL</desc></buslocation><buslocation>  <bus_id>809</bus_id>  <route_id>9</route_id>  <longitude>-104.60911333</longitude>  <latitude>50.450425</latitude>  <bearing>0</bearing>  <desc>ALBERT PARK</desc></buslocation><buslocation>  <bus_id>587</bus_id>  <route_id>1</route_id>  <longitude>-104.61690667</longitude>  <latitude>50.45040833</latitude>  <bearing>0</bearing>  <desc>BROAD NORTH</desc></buslocation><buslocation>  <bus_id>601</bus_id>  <route_id>4</route_id>  <longitude>-104.61521833</longitude>  <latitude>50.450115</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>606</bus_id>  <route_id>7</route_id>  <longitude>-104.572745</longitude>  <latitude>50.4472</latitude>  <bearing>0</bearing>  <desc>WHIT. PARK</desc></buslocation><buslocation>  <bus_id>609</bus_id>  <route_id>8</route_id>  <longitude>-104.606915</longitude>  <latitude>50.45030833</latitude>  <bearing>0</bearing>  <desc>EASTVIEW</desc></buslocation><buslocation>  <bus_id>610</bus_id>  <route_id>8</route_id>  <longitude>-104.62150333</longitude>  <latitude>50.40466167</latitude>  <bearing>0</bearing>  <desc>EASTVIEW</desc></buslocation><buslocation>  <bus_id>611</bus_id>  <route_id>7</route_id>  <longitude>-104.638555</longitude>  <latitude>50.40543</latitude>  <bearing>0</bearing>  <desc>WHIT. PARK</desc></buslocation><buslocation>  <bus_id>619</bus_id>  <route_id>40</route_id>  <longitude>-104.61%s3055</longitude>  <latitude>50.45%s10574</latitude>  <bearing>0</bearing>  <desc>ALBERT NORTH</desc></buslocation><buslocation>  <bus_id>621</bus_id>  <route_id>1</route_id>  <longitude>-104.60632</longitude>  <latitude>50.45148667</latitude>  <bearing>0</bearing>  <desc>BROAD NORTH</desc></buslocation><buslocation>  <bus_id>622</bus_id>  <route_id>10</route_id>  <longitude>-104.60716667</longitude>  <latitude>50.450365</latitude>  <bearing>0</bearing>  <desc>RCMP</desc></buslocation><buslocation>  <bus_id>623</bus_id>  <route_id>40</route_id>  <longitude>-104.64537167</longitude>  <latitude>50.49780167</latitude>  <bearing>0</bearing>  <desc>ALBERT NORTH</desc></buslocation><buslocation>  <bus_id>627</bus_id>  <route_id>1</route_id>  <longitude>-104.68684167</longitude>  <latitude>50.45581167</latitude>  <bearing>0</bearing>  <desc>BROAD NORTH</desc></buslocation><buslocation>  <bus_id>628</bus_id>  <route_id>2</route_id>  <longitude>-104.612415</longitude>  <latitude>50.45045167</latitude>  <bearing>0</bearing>  <desc>ARGYLE PARK</desc></buslocation><buslocation>  <bus_id>630</bus_id>  <route_id>40</route_id>  <longitude>-104.645335</longitude>  <latitude>50.40772</latitude>  <bearing>0</bearing>  <desc>ALBERT NORTH</desc></buslocation><buslocation>  <bus_id>639</bus_id>  <route_id>2</route_id>  <longitude>-104.60656</longitude>  <latitude>50.44876</latitude>  <bearing>0</bearing>  <desc>ARGYLE PARK</desc></buslocation></buslocations>""" %(random.randint(100,999),random.randint(100,999))
            #<buslocations><buslocation>  <bus_id>640</bus_id>  <route_id>7</route_id>  <longitude>-104.552536011</longitude>  <latitude>50.4599685669</latitude>  <bearing>0</bearing>  <desc>WHIT. PARK</desc></buslocation><buslocation>  <bus_id>609</bus_id>  <route_id>1</route_id>  <longitude>-104.599189758</longitude>  <latitude>50.4769058228</latitude>  <bearing>0</bearing>  <desc>DIEPPE</desc></buslocation><buslocation>  <bus_id>643</bus_id>  <route_id>4</route_id>  <longitude>-104.610832214</longitude>  <latitude>50.424041748</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>614</bus_id>  <route_id>13</route_id>  <longitude>-104.65259552</longitude>  <latitude>50.4635429382</latitude>  <bearing>0</bearing>  <desc>MOUNT ROYAL</desc></buslocation><buslocation>  <bus_id>646</bus_id>  <route_id>11</route_id>  <longitude>-104.624961853</longitude>  <latitude>50.4224586487</latitude>  <bearing>0</bearing>  <desc>NORMANVIEW</desc></buslocation><buslocation>  <bus_id>592</bus_id>  <route_id>13</route_id>  <longitude>-104.636581421</longitude>  <latitude>50.4382019043</latitude>  <bearing>0</bearing>  <desc>S. LAKEVIEW</desc></buslocation><buslocation>  <bus_id>593</bus_id>  <route_id>7</route_id>  <longitude>-104.636878967</longitude>  <latitude>50.4085617065</latitude>  <bearing>0</bearing>  <desc>WHIT. PARK</desc></buslocation><buslocation>  <bus_id>626</bus_id>  <route_id>9</route_id>  <longitude>-104.629707336</longitude>  <latitude>50.412109375</latitude>  <bearing>0</bearing>  <desc>ALBERT PARK</desc></buslocation><buslocation>  <bus_id>599</bus_id>  <route_id>4</route_id>  <longitude>-104.653358459</longitude>  <latitude>50.476978302</latitude>  <bearing>0</bearing>  <desc>WALSH ACRES</desc></buslocation><buslocation>  <bus_id>600</bus_id>  <route_id>10</route_id>  <longitude>-104.572471619</longitude>  <latitude>50.4400253296</latitude>  <bearing>0</bearing>  <desc>WOOD. GROVE</desc></buslocation><buslocation>  <bus_id>635</bus_id>  <route_id>11</route_id>  <longitude>-104.664428711</longitude>  <latitude>50.4625701904</latitude>  <bearing>0</bearing>  <desc>NORMANVIEW</desc></buslocation><buslocation>  <bus_id>604</bus_id>  <route_id>3</route_id>  <longitude>-104.647598267</longitude>  <latitude>50.4764175415</latitude>  <bearing>0</bearing>  <desc>SHERWOOD</desc></buslocation><buslocation>  <bus_id>637</bus_id>  <route_id>3</route_id>  <longitude>-104.592407227</longitude>  <latitude>50.4156990051</latitude>  <bearing>0</bearing>  <desc>UNIVERSITY</desc></buslocation><buslocation>  <bus_id>638</bus_id>  <route_id>1</route_id>  <longitude>-104.646499634</longitude>  <latitude>50.4551429749</latitude>  <bearing>0</bearing>  <desc>BROAD NORTH</desc></buslocation><buslocation>  <bus_id>607</bus_id>  <route_id>5</route_id>  <longitude>-104.61%s3055</longitude>  <latitude>50.45%s10574</latitude>  <bearing>130</bearing>  <desc>UNIV PARK</desc></buslocation><buslocation>  <bus_id>619</bus_id>  <route_id>2</route_id>  <longitude>-104.785539055</longitude>  <latitude>50.6890279574</latitude>  <bearing>130</bearing>  <desc>SHERWOOD</desc></buslocation><buslocation>  <bus_id>620</bus_id>  <route_id>40</route_id>  <longitude>-104.985539055</longitude>  <latitude>50.6890279574</latitude>  <bearing>130</bearing>  <desc>SHERWOOD</desc></buslocation></buslocations>""" %(random.randint(100,999),random.randint(100,999))

        elif function == 'get_stops':
            output['response'] = self.request_stops(params['route_id'])

        elif function == 'get_path':
            output['response'] = self.request_path(params['route_id'])

        elif function == 'get_stop_times':
            output['response'] = self.request_stop_times(params['stop_id'], params['route_ids'], params['lim'])

        elif function == 'get_detours':
            output['response'] = self.request_detours()
            
        elif function == 'get_schedule':
            output['response'] = self.request_schedule(params['route_id'], params['days'])
            
        else:
            output['error'] = 'Invalid Function'
            
        return output
                
    
    def request_route(self, route_id):
        output = ''
        
        if route_id == 'all':
            all_template = Template('<routes>{{data}}</routes>')
            
            for route in self.routes:
                output += self.routes[route].render()
            
            output = all_template.render(data=output)
                
        else:
            output = self.routes[int(route_id)].render()
            
        return output.replace('  ', '').replace('\n', '').replace('\t', '')
    
    def request_stops(self, route_id):   
        output = ''

        if route_id == 'all':
            all_template = Template('<routes>{{data}}</routes>')
            
            for route in self.routes:
                output += self.routes[route].stops.render()
            
            output = all_template.render(data=output)
                
        else:
            output = self.routes[int(route_id)].stops.render()

        return output.replace('  ', '').replace('\n', '').replace('\t', '')

    def request_path(self, route_id):
        output = ''

        return self.routes[int(route_id)].path

    
    def request_bus_location(self, bus_id, timestamp): 
        output = ''
        
        if bus_id == 'all':
            return self.request_bus_locations(timestamp)
            
        else:
            return self.bus_locations[int(bus_id)].render()

    def request_bus_locations(self, timestamp): 
        output = ''
        
        self.bus_locations = {}
        output_locations = {}

        # read bus locations from db
        locations = self.database.execute("SELECT * FROM locations").fetchall()
        for location in locations:
            bus_location = BusLocation(fields_list=location)
            self.bus_locations[location[0]] = bus_location
            
            if timestamp == None or bus_location.timestamp > timestamp:
                output_locations[bus_location.bus_id] = bus_location
        
        output = TransitLive.template_locations_all.render(data=output_locations, timestamp=int(time.time()))
            
        return output

    def request_stop_times(self, stop_id, routes, limit):
        output = ''
        
        try:
            # download and parse data
            url = TransitLive.API['MAIN'] % TransitLive.API['STOP_TIMES'] % (stop_id, routes, limit)
            stoptimes_data = json.loads(urllib2.urlopen(url).read())
            #stoptimes_data = json.loads(TransitLive.stoptimes_json)

            stoptimes = []
            for element in stoptimes_data:
                stoptimes.append(StopTime(element))

            output = TransitLive.template_stoptimes.render(data=stoptimes)

        except Exception, e:
            print 'error fetching stoptimes', str(e)

        return output.replace('  ', '').replace('\n', '').replace('\t', '')

    def request_detours(self):
        output = TransitLive.template_detours.render(data=self.detours)

        return output
        
        

    def request_schedule(self, route_id, days):
        try:
            template = Template(open("templates/template_tl_route%s%s.xml" % (route_id, days)).read())
            return template.render()
            
        except IOError:
            return "Invalid route"
            
            
            
    def load_route_cache(self):
        with open(TransitLiveUpdater.DETOURS_FILE) as f2:
            s2 = pickle.loads(f2.read())
            self.detours = s2

        with open(TransitLiveUpdater.ROUTES_FILE) as f:
            s = pickle.loads(f.read())
            self.routes = s
            

        
class BusLocation:

    def __init__(self, fields_dict=None, fields_list=None):

        if fields_dict is not None:
            self.bus_id = int(fields_dict['properties']['b'])
            self.route_id = int(fields_dict['properties']['r'])
            self.latitude = float(fields_dict['geometry']['coordinates'][1])
            self.longitude = float(fields_dict['geometry']['coordinates'][0])
            self.bearing = 0 #int(fields_dict.get('bearing', ''))
            self.desc = fields_dict['properties']['line']
            self.timestamp = int(fields_dict.get('timestamp', int(time.time())))

        elif fields_list is not None:
            self.bus_id = fields_list[0]
            self.route_id =  fields_list[1]
            self.latitude = fields_list[2]
            self.longitude = fields_list[3]
            self.bearing = 0
            self.desc = fields_list[4]
            self.timestamp = fields_list[5]
        
    def render(self):
        return TransitLive.template_buslocation.render(o=self)
        
        


class Route:

    def __init__(self, fields_dict):
        
        self.route_id = int(fields_dict.get('route_id', ''))
        self.colour = fields_dict.get('colour', '')
        self.short_name = fields_dict.get('name', '').replace('+', ' ')
        self.full_name = self.short_name
        self.file_name = self.short_name

        self.stops = StopList(self.route_id) # list of Stops
        self.path = "" # list of geo coordinates (tuple)
        
    def render(self):
        return TransitLive.template_route.render(o=self)


class StopList:
    def __init__(self, route_id):
        self.route_id = route_id
        self.stops = []
        
    def append(self, stop):
        self.stops.append(stop)
    
    def render(self):
        return TransitLive.template_stops.render(o=self)
        

class Stop:

    def __init__(self, fields_dict):
       
        self.stop_id = int(fields_dict.get('stopID', ''))
        self.longitude = float(fields_dict.get('longitude', ''))
        self.latitude = float(fields_dict.get('latitude', ''))
        self.name = fields_dict.get('name', '')
        self.direction = fields_dict.get('direction', '')
        
class StopTime:

    def __init__(self, fields_dict):

        self.pred_time = fields_dict.get('pred_time', '')
        self.intersection = fields_dict.get('intersection', '')
        self.bus_id = safe_cast(fields_dict.get('bus_id', '-1'), int, -1)
        self.route_id = safe_cast(fields_dict.get('route_id', '-1'), int, -1)
        self.stop_time_id = safe_cast(fields_dict.get('stop_time_id', '-1'), int, -1)
        self.line_name = fields_dict.get('line_name', '')

class Detour:

    def __init__(self, fields_dict):
        self.stop_id = safe_cast(fields_dict.get('stop_id', '-1'), int, -1)
        self.message = fields_dict.get('message', '')
        
        
        
class TransitLiveUpdater:

    ROUTES_FILE = "cache/routes.pkl"
    DETOURS_FILE = "cache/detours.pkl"
    DATABASE = "cache/transitlive.db"

    def __init__(self, debug=False):

        import socket
    	socket.setdefaulttimeout(8)

        print  "[%s] Starting TransitLive Updater" % time.time()

        self.debug = debug
        self.bus_locations = None # dictionary (bus_id as index)
        self.routes = None # dictionary (route_id as index)
        self.detours = None

        # open database
        self.prepare_database()

        
    def prepare_database(self):

        if not os.path.exists('./cache'):
            try:
                os.makedirs('./cache')
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

        self.database = sqlite3.connect(TransitLiveUpdater.DATABASE, check_same_thread=False)
        
        self.database.execute("CREATE TABLE IF NOT EXISTS locations " \
            + "(id INTEGER PRIMARY KEY, route_id INTEGER, lat real, " \
            + "lng real, text description, timestamp INTEGER);")


    def start_updating(self):
        # launch updater threads
        self.location_thread = TransitLiveUpdater.RepeatedUpdater(
            [self.update_location_data], 1)
        
        self.route_thread = TransitLiveUpdater.RepeatedUpdater([
            self.update_detour_data, 
            self.update_route_data, 
            self.update_path_data,
            self.update_stops_data,
            self.store_route_data], 5600)
            
        self.location_thread.start()
        self.route_thread.start()

        
    def update_location_data(self):
        if self.debug: print "[%s] update_location_data" % int(time.time())
    
        # Download and parse route meta-data
        url = TransitLive.API['MAIN'] % TransitLive.API['BUS_INFO'][0]

        location_data = json.loads(urllib2.urlopen(url).read())
        #location_data = json.loads(TransitLive.bus_json)

        new_locations = {}
        old_locations = {}

        to_add = []
        to_update = []
        to_delete = []
        
        timestamp = int(time.time())

        # retrieve old locations from db
        for location in self.database.execute("SELECT * FROM locations").fetchall():
            old_locations[location[0]] = BusLocation(fields_list=location)

        # add or update locations
        for location in location_data:
            new_location = BusLocation(fields_dict=location)            
            new_locations[new_location.bus_id] = new_location

            old_location = old_locations.get(new_location.bus_id)

            if old_location == None:
                to_add.append(new_location)

            elif haversine.distance(
                (new_location.latitude, new_location.longitude), 
                (old_location.latitude, old_location.longitude)) >= 0.00100325585:

                to_update.append(new_location)

        # delete removed buses
        for bus_id in old_locations:
            if bus_id not in new_locations:
                to_delete.append(old_locations[bus_id])

        # execute add
        for location in to_add:
            self.database.execute("INSERT INTO locations VALUES (?, ?, ?, ?, ?, ?)", (
                location.bus_id, 
                location.route_id, 
                location.latitude,
                location.longitude,  
                location.desc,
                timestamp))

        # execute update
        for location in to_update:
            self.database.execute("UPDATE locations SET lat=?, lng=?, timestamp=? WHERE id=?", ( 
                location.latitude, 
                location.longitude, 
                timestamp,
                location.bus_id))

        # execute deletes
        for location in to_delete:
            print "DELETE", location.bus_id
            self.database.execute("DELETE FROM locations WHERE id=?", (location.bus_id, ))

        self.database.commit();

            
        

    def update_route_data(self):
        if self.debug: print "[%s] update_route_data" % int(time.time())

        # Download and parse route meta-data
        url = TransitLive.API['MAIN'] % TransitLive.API['ROUTE_INFO'][0]

        route_data = json.loads(urllib2.urlopen(url).read())
        #route_data = json.loads(TransitLive.route_json)

        # Instantiate routes and store
        self.routes = {}

        for element in route_data:
            new_route = Route(element)
            
            self.routes[new_route.route_id] = new_route

        # Write to file
        # TODO: remove when also updating stops
        # s = pickle.dumps(self.routes)
        # with open(TransitLiveUpdater.ROUTES_FILE, 'w') as f:
        #     f.write(s)

    def update_path_data(self):
        if self.debug: print "[%s] update_path_data" % int(time.time())

        if len(self.routes) == 0:
            print "Routes not yet defined!"
            return # TODO: Exception system 

        for route_id in self.routes:
            if route_id == "detours":
                continue

            # Download and parse path data
            url = (TransitLive.API['MAIN'] % TransitLive.API['ROUTE_PATHS']) % route_id

            path_data = json.loads(urllib2.urlopen(url).read())

            path_string = ""
            for latlng in path_data["coordinates"]:
                path_string = path_string + "%s,%s;" % (latlng[0], latlng[1])

            self.routes[route_id].path = path_string

    def update_stops_data(self):
        if self.debug: print "[%s] update_stops_data" % int(time.time())

        if len(self.routes) == 0:
            print "Routes not yet defined!"
            return # TODO: Exception system

        url = (TransitLive.API['MAIN'] % TransitLive.API['STOPS'])

        stops_data = json.loads(urllib2.urlopen(url).read())

        for stop in stops_data:
            properties = stop["properties"]
            coordinates = stop["geometry"]["coordinates"]

            new_stop = Stop({
                'stopID': properties["id"],
                'name': properties["name"],
                'direction': properties["dir"],
                'longitude': coordinates[0],
                'latitude': coordinates[1],
            })

            for route_id in properties["r"]:
                if (route_id not in self.routes):
                    continue

                self.routes[route_id].stops.stops.append(new_stop)


    def update_detour_data(self):
        if self.debug: print "[%s] update_detour_data" % int(time.time())

        url = TransitLive.API['MAIN'] % TransitLive.API['DETOURS']

        detour_data = json.loads(urllib2.urlopen(url).read())
        #detour_data = json.loads(TransitLive.detours_json)

        self.detours = []
        
        for element in detour_data:
            new_detour = Detour(element)

            self.detours.append(new_detour)

        # Write to file
        if self.debug: print "[%s] writing detours to file" % int(time.time())
        s = pickle.dumps(self.detours)
        with open(TransitLiveUpdater.DETOURS_FILE, 'w') as f:
            f.write(s)
                
    def store_route_data(self):
        # Write to file
        if self.debug: print "[%s] writing routes to file" % int(time.time())
        s = pickle.dumps(self.routes)
        with open(TransitLiveUpdater.ROUTES_FILE, 'w') as f:
            f.write(s)
            
    class RepeatedUpdater(threading.Thread):
        
        def __init__(self, functions, interval):
            threading.Thread.__init__(self)

            self.interval = interval
            self.functions = functions
            
            self.setDaemon(True)
            self.stop = False
        
        def run(self):
            
            while not self.stop:
                try:
                    for function in self.functions:
                        function()

                except Exception, e:
                    print "\n", "-"*80, "\n"
                    print "Error in updater thread"
                    traceback.print_exc()
                    print "\n", "-"*80, "\n"
                        
                time.sleep(self.interval)
                


    @staticmethod
    def parse_repeated(data, split_param):

        # Convert parameter string into segments on split_param
        segments = data.split(split_param)

        # Return split_param to the segments and remove any preceding data
        segments = [split_param + segment for segment in segments if segment[0] == '=']

        # Parse each segment's parameters
        segments = [segment.split('&') for segment in segments]

        for i, segment in enumerate(segments):
            params = [p.split('=') for p in segment if p != '']
            segments[i] = dict((p[0],p[1]) for p in params)

        return segments


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default        


if __name__ == "__main__":
    import transitlive

    tlu = transitlive.TransitLiveUpdater(debug=True)
    tlu.start_updating()

    try:
        while threading.active_count() > 0:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        tlu.location_thread.stop = True
        tlu.route_thread.stop = True
       
    
    tl = TransitLive(debug=True)

    print tl.request_bus_locations()

    #print tl.routes[3]
    #print tl.request_stop_times("1544", "3,10,12", "30")
    #print tl.request_detours()
    
    #time.sleep(20)
