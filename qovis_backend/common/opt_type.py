data = """
Project	B	P	6946	*
Filter	B	F	1614	*
Join	L	J	2470	*
SerializeFromObject	L	SFO	1903	
InMemoryRelation	L	IMR	1607	*
ExternalRDD	L	ERD	1326	*
Aggregate	L	A	298	*
SubqueryAlias	L	SA	212	
View	L	V	212	
UnresolvedRelation	L	UR	51	*
LocalRelation	L	LR	4	
LogicalQueryStage	P	LQS	2287	
HashAggregate	P	HA	1922	*
Sort	P	S	1661	*
BroadcastHashJoin	P	BHJ	1179	*
SortMergeJoin	P	SMJ	1034	*
ShuffleExchange	P	SE	728	*
ShuffleQueryStage	P	SQS	624	
ExternalRDDScan	P	ES	577	*
BroadcastQueryStage	P	BQS	392	
InputAdapter	P	IA	193	
WholeStageCodegen	P	WSC	157	
BroadcastExchange	P	BE	105	*
AQEShuffleRead	P	ASR	88	
InMemoryTableScan	P	IMS	5	*
"""

OPT_INFO_MAP = {}
for line in data.splitlines():
    if line == '':
        continue
    name_, type_, alias, cnt, is_imp = line.split('\t')
    OPT_INFO_MAP[name_] = {
        'name': name_,
        'type': type_,
        'alias': alias,
        'is_imp': is_imp == '*'
    }


def get_opt_info(name):
    return OPT_INFO_MAP[name]
