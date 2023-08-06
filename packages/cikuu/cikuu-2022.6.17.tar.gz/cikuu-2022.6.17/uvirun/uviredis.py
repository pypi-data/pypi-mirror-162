# 2022.8.6 cp from stream/uvirun.py  | uvicorn uviredis:app --host 0.0.0.0 --port 16379 --reload 
import json,requests,hashlib,os,time,redis,fastapi, uvicorn , random,asyncio, platform 
from fastapi.responses import HTMLResponse
app	= globals().get('app', fastapi.FastAPI()) #from uvirun import *
if not hasattr(redis,'r'): 
	redis.r		= redis.Redis(host=os.getenv("rhost", "127.0.0.1" if "Windows" in platform.system() else "172.17.0.1"), port=int(os.getenv('rport', 6379)), db=int(os.getenv('rdb', 0)), decode_responses=True) 

from fastapi.staticfiles import StaticFiles #http://localhost/static/index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/redis/info')
def redis_info(): return redis.r.info()

@app.get('/redis/rg_pyexecute')
def rg_pyexecute(cmd:str="GB().flatmap(lambda x: execute('hvals', x['key']) ).countby().run('rid-230537:tid-1:uid-*')", name:str = 'rg.eval'):
	''' GB().map(lambda x: x['value']).flatmap(lambda x: x.split()).countby().run('sent:*')	'''
	res = redis.r.execute_command(*["RG.PYEXECUTE",cmd if cmd.startswith("GB().") else f"GB().{cmd}"])
	return [ eval(line) for line in res[0] ] if res and len(res) > 0 else None 

@app.post('/redis/mexec')
def command_execute_mul(cmds:dict={"test1":["get","hello"], "snt-search": "FT.SEARCH ftsnt '@cola:[0.5,0.9]' limit 0 2".split(),}):
	''' execute sql-like-scripts over redis '''
	res = {} 
	for name, args in cmds.items():
		try:
			args = args if isinstance(args, list) else args.split()
			res[name] = mapf.get(name.split(":")[0], lambda x: x)(redis.r.execute_command(*args))
		except Exception as e:
			res[name] = str(e)
	return res 

@app.get('/redis/hgetall')
def redis_hgetall(key:str='rid-230537:tid-1', JSONEachRow:bool=False): 
	return redis.r.hgetall(key) if not JSONEachRow else [{"key":k, "value":v} for k,v in redis.r.hgetall(key).items()]

@app.get('/redis/hgetalls')
def redis_hgetalls(pattern:str='rid-*'):
	''' rid-230537:tid-1:uid-* | for JSONEachRow , added 2022.5.17 '''
	return { key: redis.r.hgetall(key) for key in redis.r.keys(pattern) if redis.r.type(key) == 'hash' }

@app.get('/redis/zrangelist')
def redis_zrangelist(pattern:str='stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-*', withscores:bool=False):
	''' stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-fill-11  '''
	return { key: list(redis.r.zrange(key,0,-1, withscores=withscores)) for key in redis.r.keys(pattern) if redis.r.type(key) == 'zset' }

@app.get('/redis/keys_hgetall')
def redis_hgetalls_map(pattern:str='rid-230537:tid-0:uid-*'):
	''' added 2022.5.14 '''
	return [] if pattern.startswith("*") else [{"key": key, "value":redis.r.hgetall(key)} for key in redis.r.keys(pattern)]

@app.get('/redis/keys')
def redis_keys(pattern:str='rid-230537:tid-0:uid-*'):	return [] if pattern.startswith("*") else [{"key": key} for key in redis.r.keys(pattern)] 
@app.get('/redis/keys_hget')
def redis_keys_hget(pattern:str='rid-230537:tid-0:uid-*', hkey:str='rid', jsonloads:bool=False):
	''' added 2022.5.15 '''
	if pattern.startswith("*"): return []
	return [{"key": key, "value": ( res:=redis.r.hget(key, hkey), json.loads(res) if res and jsonloads else res)[-1] } for key in redis.r.keys(pattern)]

@app.get('/redis/hget')
def redis_hget(key:str='config:rid-10086:tid-1', hkey:str='rid', jsonloads:bool=False):
	res = redis.r.hget(key, hkey)
	return json.loads(res) if res and jsonloads else res  
@app.post('/redis/execute_command')
def redis_execute_command(cmd:list='zrevrange rid-230537:snt_cola 0 10 withscores'.split()):	return redis.r.execute_command(*cmd)
@app.post('/redis/execute_commands')
def redis_execute_commands(cmds:list=["info"]):	return [redis.r.execute_command(cmd) for cmd in cmds]

@app.post('/redis/xinfo')
def redis_xinfo(keys:list=["rid-230537:xwordidf","xessay"], name:str="last-entry"):	return { key: redis.r.xinfo_stream(key)[name]  for key in keys }
@app.get('/redis/delkeys')
def redis_delkeys(pattern:str="rid-230537:*"): return [redis.r.delete(k) for k in redis.r.keys(pattern)]
@app.post('/redis/delkeys')
def redis_delkeys_list(patterns:list=["rid-230537:*","essay:rid-230537:*"]): return [ redis_delkeys(pattern) for pattern in patterns ]
@app.get('/redis/delete')
def redis_delete(key:str="stroke:ap-{ap}:page-{page}:pen-{pen}:item-{item}"): return redis.r.delete(key)
@app.post('/redis/xadd')
def redis_xadd(name:str="xitem", arr:dict={"rid":"230537", "uid":"1001", "tid":0, "type":"fill", "label":"open the door"}): return redis.r.xadd(name, arr )
@app.get('/redis/xrange')
def redis_xrange(name:str='xitem', min:str='-', max:str="+", count:int=1): return redis.r.xrange(name, min=min, max=max, count=count)
@app.get('/redis/lrange')
def redis_lrange(name:str='stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-fill-11', start:int=0, end:int=-1): return redis.r.lrange(name, start, end)
@app.get('/redis/xrevrange')
def redis_xrevrange(name:str='xlog', min:str='-', max:str="+", count:int=1): return redis.r.xrevrange(name, min=min, max=max, count=count)
@app.get('/redis/zrevrange')
def redis_zrevrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrevrange(name, start, end, withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrevrange(name, start, end, withscores)]
@app.get('/redis/zrange')
def redis_zrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrange(name, start, end, withscores=withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrange(name, start, end, withscores=withscores)]
@app.get('/redis/set')
def redis_set(key:str='rid-230537:config',value:str=""): return redis.r.set(key, value) 
@app.post('/redis/hset')
def redis_hset(arr:dict={}, key:str='rid-10086:tid-1:uid-pen-zz', k:str="label", v:str="v"):	return redis.r.hset(key, k, v, arr) 
@app.post('/redis/hdel')
def redis_hdel(keys:list=[], name:str='one'): return redis.r.hdel(name, *keys) 
@app.get('/redis/hdel')
def redis_hdel_get(key:str='one', hkey:str='k,k1' , sep:str=','): return [redis.r.hdel(key, k) for k in hkey.split(sep)]
@app.post('/redis/zadd')
def redis_zadd(arr:dict={}, key:str='rid-230537:config'): return redis.r.zadd(key, arr) 
@app.get('/redis/xlen')
def redis_xlen(key:str='xsnt',ts:bool=False): return redis.r.xlen(key) if not ts else {"time":time.time(), "Value":redis.r.xlen(key)}
@app.get('/redis/zsum')
def redis_zsum(key='rid-230537:essay_wordnum',ibeg=0, iend=-1): return sum([v for k,v in redis.r.zrevrange(key, ibeg, iend, True)])

@app.post('/redis/join_even_odd')
def redis_even_odd(arr:list=['even line','odd line'], asdic:bool=False): return dict(zip(arr[::2], arr[1::2])) if asdic else list(zip(arr[::2], arr[1::2]))

four_int = lambda four, denom=100: [int( int(a)/denom) for a in four]
xy = lambda four : [f"{a},{b}" for a in range(four[0], four[2]+2) for b in range( four[1], four[3] + 2) ] # xy_to_item
@app.post('/redis/penly/xy_to_item')
def penly_xy_to_items(arr:list=[[620,170,1800,370,"zh_CN-name"],[200,650,1150,880,"select-1:A"],[1300,650,2160,880,"select-1:B"],[2400,650,3520,880,"select-1:C"],[3550,650,4700,880,"select-1:D"],[200,1020,1160,1250,"select-2:A"],[1300,1020,2160,1250,"select-2:B"],[2400,1020,3520,1250,"select-2:C"],[3550,1020,4700,1250,"select-2:D"],[200,1400,1290,1590,"select-3:A"],[1360,1400,2160,1590,"select-3:B"],[2400,1400,3520,1590,"select-3:C"],[3550,1400,4760,1590,"select-3:D"],[200,1750,1160,1950,"select-4:A"],[1300,1750,2160,1950,"select-4:B"],[2400,1750,3520,1950,"select-4:C"],[3550,1750,4700,1950,"select-4:D"],[200,2100,1160,2320,"select-5:A"],[1300,2100,2160,2320,"select-5:B"],[2400,2100,3520,2320,"select-5:C"],[3550,2100,4700,2320,"select-5:D"],[200,2450,1160,2670,"select-6:A"],[1300,2450,2160,2670,"select-6:B"],[2400,2450,3400,2670,"select-6:C"],[3550,2450,4700,2670,"select-6:D"],[200,2800,1160,3040,"select-7:A"],[1300,2800,2260,3040,"select-7:B"],[2400,2800,3420,3040,"select-7:C"],[3550,2800,4700,3040,"select-7:D"],[200,3180,1160,3380,"select-8:A"],[1300,3200,2160,3380,"select-8:B"],[2400,3180,3520,3380,"select-8:C"],[3550,3180,4700,3380,"select-8:D"],[200,3530,1210,3750,"select-9:A"],[1300,3530,2360,3750,"select-9:B"],[2550,3530,3520,3750,"select-9:C"],[3550,3530,4700,3750,"select-9:D"],[200,3900,1160,4120,"select-10:A"],[1300,3900,2200,4120,"select-10:B"],[2400,3900,3520,4120,"select-10:C"],[3550,3900,4700,4120,"select-10:D"],[2580,4260,4380,4500,"fill-11"],[3000,4550,5240,4790,"zh_CN-fill-12"],[460,5050,620,5200,"cross-13:No_1"],[630,5050,950,5200,"cross-13:reliable_2"],[960,5050,1250,5200,"cross-13:figures_3"],[1260,5050,1390,5200,"cross-13:are_4"],[1400,5050,1780,5200,"cross-13:available_5"],[1790,5050,1930,5200,"cross-13:for_6"],[1940,5050,2220,5200,"cross-13:money_7"],[2230,5050,2750,5200,"cross-13:accumulated_8"],[2760,5050,2960,5200,"cross-13:from_9"],[2980,5050,3320,5200,"cross-13:popcorn_10"],[3330,5050,3530,5200,"cross-13:sales_11"],[3590,5050,3720,5200,"cross-13:but_13"],[3740,5050,3900,5200,"cross-13:film_14"],[3930,5050,4100,5200,"cross-13:fans_15"],[4120,5050,4420,5200,"cross-13:usually_16"],[4430,5050,4800,5200,"cross-13:consume_17"],[4820,5050,4870,5200,"cross-13:a_18"],[4880,5050,5000,5200,"cross-13:lot_19"],[5020,5050,5120,5200,"cross-13:of_20"],[5130,5050,5300,5200,"cross-13:this_21"],[310,5300,530,5500,"cross-13:salty_22"],[550,5300,730,5500,"cross-13:food_23"],[770,5300,1170,5500,"cross-13:especially_25"],[1200,5300,1400,5500,"cross-13:when_26"],[1440,5300,1800,5500,"cross-13:watching_27"],[1830,5300,1870,5500,"cross-13:a_28"],[1890,5300,2100,5500,"cross-13:tense_29"],[2110,5300,2390,5500,"cross-13:thriller_30"],[340,5920,1860,6290,"branstorm-14-1"],[2060,5920,3530,6290,"branstorm-14-2"],[3790,5920,5220,6290,"branstorm-14-3"],[480,6670,4880,6950,"essay15-1"],[499,7100,4880,7340,"zh_CN-question-1"],[4990,7140,5280,7390,"submit-1:0"],[310,7400,810,7700,"hands:0"],[3500,7450,3880,7700,"select-25:A"],[3960,7450,4270,7700,"select-25:B"],[4320,7450,4670,7700,"select-25:C"],[4720,7450,5050,7700,"select-25:D"],[5000,6720,5270,6940,"translate:0"],[420,470,610,580,"evidence-1:The_1"],[1020,470,1130,580,"evidence-1:of_2"],[1140,470,1370,580,"evidence-1:blood_3"],[1380,470,1610,580,"evidence-1:made_4"],[1620,470,1760,580,"evidence-1:the_5"],[1770,470,1910,580,"evidence-1:girl_6"],[1920,470,2090,580,"evidence-1:feel_7"],[2100,470,2280,580,"evidence-1:sick_8"],[2290,470,2450,580,"evidence-1:and_9"],[2460,470,2590,580,"evidence-1:she_10"],[2600,470,2860,580,"evidence-1:began_11"],[2870,470,2960,580,"evidence-1:to_12"],[2970,470,3120,580,"evidence-1:cry_13"],[600,500,1000,650,"display-select-1"],[3200,850,3600,1000,"display-select-2"],[760,1220,1160,1370,"display-select-3"],[3510,1570,3910,1720,"display-select-4"],[1080,1940,1480,2090,"display-select-5"],[430,2300,830,2450,"display-select-6"],[1550,2660,1950,2810,"display-select-7"],[1260,3000,1660,3150,"display-select-8"],[3670,3370,4070,3520,"display-select-9"],[480,3720,880,3870,"display-select-10"],[2430,5360,5240,5490,"display-cross-13"]], denom:int=100,key:str="page:1713.537.31.92:xy_to_item"): 
	''' submit data into the permanent store, updated 2021.10.8 '''
	return [redis.r.hset(key, k, tag) for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1/denom), int(y1/denom), int(x2/denom), int(y2/denom)) )]

@app.post('/redis/penly/mock_send_stroke')
def penly_mock_send_stroke(strokes:list=["quick:1713.537.31.92:BP2-0L3-03I-4V:1658389523.028:3752,1389,100,1658389523 3738,1395,428,1658389523 3719,1429,720,1658389523 3731,1602,832,1658389523 3797,1605,848,1658389523 3845,1551,808,1658389523 3876,1375,708,1658389523 3840,1330,748,1658389523 3782,1331,740,1658389523",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1658389718.028:2641,2157,100,1658389718 2623,2160,624,1658389718 2611,2192,700,1658389718 2607,2290,728,1658389718 2639,2315,796,1658389718 2711,2279,760,1658389718 2756,2109,756,1658389718 2688,2078,552,1658389718",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1658389718.48:2604,2446,100,1658389718 2595,2482,700,1658389718 2606,2560,744,1658389718 2757,2442,788,1658389718 2609,2450,100,1658389718 2579,2508,100,1658389718",
"quick:1713.537.31.89:BP2-0L3-03I-4V:1658389981.072:3766,1648,676,1658389981 3755,1680,688,1658389981 3767,1811,772,1658389981 3807,1813,684,1658389981 3851,1790,708,1658389981 3881,1737,696,1658389981 3870,1682,724,1658389981 3836,1637,748,1658389981 3807,1635,748,1658389981 3796,1647,100,1658389981 3798,1643,100,1658389981",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688058.044:3781,1060,231,1659688058 3771,1058,477,1659688058 3759,1062,704,1659688058 3752,1097,732,1659688058 3732,1139,736,1659688058 3731,1178,780,1659688058 3747,1200,808,1659688058 3778,1208,824,1659688058 3818,1194,772,1659688058 3864,1146,792,1659688058 3889,1091,772,1659688058 3875,1016,756,1659688058 3844,1006,772,1659688058 3808,1008,792,1659688058 3786,1023,640,1659688058 3777,1030,165,1659688058",
#open
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688120.028:3747,4355,100,1659688120 3746,4355,141,1659688120 3747,4355,516,1659688120 3745,4364,640,1659688120 3745,4384,724,1659688120 3759,4408,752,1659688120 3768,4412,780,1659688120 3770,4402,744,1659688120 3780,4381,736,1659688120 3785,4366,768,1659688120 3782,4353,784,1659688120 3781,4336,792,1659688120 3776,4327,772,1659688120 3768,4330,764,1659688120 3760,4334,776,1659688120 3759,4337,712,1659688120 3750,4350,188,1659688120 3750,4361,188,1659688120",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688121.192:3810,4319,100,1659688121 3816,4315,198,1659688121 3819,4316,668,1659688121 3821,4317,740,1659688121 3822,4321,784,1659688121 3825,4328,812,1659688121 3833,4357,820,1659688121 3817,4492,840,1659688121 3813,4490,453,1659688121 3806,4479,104,1659688121",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688121.524:3821,4326,100,1659688121 3823,4324,412,1659688121 3835,4324,648,1659688121 3853,4331,708,1659688121 3868,4353,756,1659688121 3871,4378,760,1659688121 3865,4394,796,1659688121 3843,4406,756,1659688121 3820,4411,236,1659688121",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688122.02:3891,4369,100,1659688122 3892,4366,501,1659688122 3898,4367,660,1659688122 3902,4368,736,1659688122 3909,4370,784,1659688122 3921,4368,804,1659688122 3935,4360,792,1659688122 3939,4350,728,1659688122 3945,4339,776,1659688122 3937,4336,796,1659688122 3933,4330,816,1659688122 3924,4328,816,1659688122 3914,4331,840,1659688122 3906,4341,856,1659688122 3901,4359,856,1659688122 3902,4383,852,1659688122 3906,4409,852,1659688122 3922,4418,880,1659688122 3928,4417,868,1659688122 3935,4407,820,1659688122 3942,4390,100,1659688122 3944,4373,100,1659688122",
"quick:1713.537.31.92:BP2-0L3-03I-4V:1659688122.588:3978,4319,100,1659688122 3976,4319,277,1659688122 3980,4325,540,1659688122 3979,4329,728,1659688122 3981,4344,828,1659688122 3980,4368,844,1659688122 3977,4385,844,1659688122 3979,4390,880,1659688122 3978,4389,872,1659688122 3977,4383,816,1659688122 3980,4364,740,1659688122 3984,4340,736,1659688122 3986,4330,764,1659688122 3991,4325,780,1659688122 4003,4318,796,1659688122 4011,4314,816,1659688122 4023,4313,816,1659688122 4029,4315,832,1659688122 4031,4317,816,1659688122 4032,4321,828,1659688122 4031,4323,872,1659688122 4032,4327,876,1659688122 4032,4333,900,1659688123 4033,4358,876,1659688123 4033,4373,868,1659688123 4033,4386,856,1659688123 4029,4405,860,1659688123 4040,4417,888,1659688123 4036,4416,872,1659688123 4034,4411,744,1659688123 4027,4399,252,1659688123 3994,4370,252,1659688123",
], name:str='pen_stroke'):
	''' mock sending strokes to redis:pen_stroke '''
	redis.r.delete("stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-fill-11") # open stroke
	for s in strokes :  redis.r.publish(name, s ) 
	return 'Finished sending data: ' + time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))  

@app.get('/redis/penly/svg', response_class=HTMLResponse)
def penly_svg(lkey:str="stroke:ap-quick:page-1713.537.31.105:pen-BP2-1E1-03P-MK:item-zh_CN-fill-7", start:int=0, end:int=-1, color:str='black', width:int=10, full:bool=True): 
	''' <svg viewBox="0 0 5600 7920">
  <polyline points="26,90 23,89 25,89 24,88 24,90 24,92 20,98 17,121 23,144 35,159 48,162 73,142 87,108 89,76 80,56 58,51 31,66 15,99 13,117" style="fill:none;stroke:blue;stroke-width:15" />
  <polyline points="97,54 94,52 97,47 109,44 110,41 111,42 112,43 112,41 116,42 114,44 117,53 124,113 134,167 140,174 153,143 164,109 167,83 170,64 172,62 166,61 155,59" style="fill:none;stroke:black;stroke-width:15" />
  <polyline points="175,108 178,114 188,118 199,121 215,120 242,112 247,102 248,92 247,84 237,75 219,72 211,77 205,95 199,125 200,153 210,171 220,173 247,155 273,116 290,89 297,78 298,71 296,64 294,61 294,63 295,64 296,66 297,68 299,76 302,107 309,145 310,156 310,145 312,118 319,91 325,86 327,89 332,99 340,105" style="fill:none;stroke:black;stroke-width:15" />
  <polyline points="410,81 423,50 399,62 381,85 377,135 384,166 392,173 405,174 424,150 444,134 448,126 449,125 447,125 448,125 447,125 448,128 448,131 450,141 456,157 467,166 482,169 489,149 492,133 490,117 478,102 450,91 445,94 444,99 459,110 481,102" style="fill:none;stroke:black;stroke-width:15" />
  <polyline points="527,89 532,82 532,79 534,81 535,84 534,102 526,134 524,140 526,139 531,132 535,113 546,90 558,75 568,64 569,64 571,67 570,71 577,97 578,114 578,117 579,117 582,114 586,108 594,91 604,74 613,60 614,58 615,59 616,63 618,82 615,111 616,133 614,162 614,156 625,124" style="fill:none;stroke:black;stroke-width:15" />
  <polyline points="655,84 655,87 659,93 668,96 681,95 696,90 710,82 718,70 718,57 715,52 709,48 698,47 670,57 655,96 652,145 681,175 710,174 724,168 728,160 733,128" style="fill:none;stroke:black;stroke-width:15" />
</svg> '''
	def polyline(stroke:str='903,554,100,1656990923 911,559,161,1656990923 917,552,201,1656990923', xmin:int=0, ymin:int=0): 
		res = []
		for s in stroke.split(' '): 
			arr = s.split(',')
			if len(arr) >= 4:  res.append( f"{int(arr[0]) - xmin},{int(arr[1]) - ymin}") 
		plist = " ".join(res)
		return f'<polyline points="{plist}" style="fill:none;stroke:{color};stroke-width:{width}" />'
	strokes = redis.r.lrange(lkey, start, end)
	xypts	= [ ar.split(',') for stroke in strokes for ar in stroke.split(':')[-1].split(' ')]
	if not xypts: return ""
	x_min	= min([int(x) for x,y,p,t in xypts ])
	x_max	= max([int(x) for x,y,p,t in xypts ])
	y_min	= min([int(y) for x,y,p,t in xypts ])
	y_max	= max([int(y) for x,y,p,t in xypts ])
	polylines = "\n".join([ polyline(stroke, x_min, y_min) for stroke in strokes ])
	return HTMLResponse(content=f'<svg viewBox="0 0 {5600 if full else x_max - x_min} {7920 if full else y_max - y_min}">{polylines}</svg>')

if __name__ == '__main__':	
	#print(penly_svg("stroke:ap-quick:pen-BP2-0L3-03I-4V:page-1713.537.31.90:item-fill-58")) 
	print(redis_info())
	uvicorn.run(app, host='0.0.0.0', port=16379)