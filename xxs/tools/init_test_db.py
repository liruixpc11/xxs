# coding=UTF-8

import collections
import itertools
import uuid
import random
from datetime import datetime, timedelta
from xxs.models import *

db_factory = DbFactory()
db_factory.init_schema()
with db_factory.create_session() as session:
    task = Task(name=u'测试任务')
    session.add(task)

    group_count = 10
    groups = []
    executions = []
    for i in range(group_count):
        group = Group(name=u'第{:02d}组'.format(i + 1))
        groups.append(group)
        session.add(group)

        execution = Execution(group=group, task=task)
        executions.append(execution)
        session.add(execution)

    camp_count = 10
    camp_desc_list = []
    camps = []
    for i in range(camp_count):
        camp_desc = CampDesc(name='Flag-{:02d}'.format(i + 1),
                             type=CampTypes.File,
                             target_node='Node-{:02d}'.format(i + 1),
                             score=100,
                             service_port=80,
                             service_type='wordpress')
        camp_desc_list.append(camp_desc)
        session.add(camp_desc)

        camps.append([])
        for j, execution in enumerate(executions):
            camp = TeamCamp(execution=execution, desc=camp_desc,
                            target_node=u'{}.{}'.format(execution.group.name, camp_desc.target_node),
                            ip='192.168.{}.1{}'.format(j + 1, i + 1))
            camps[-1].append(camp)
            session.add(camp)

    begin_time = datetime.now()
    round_delta = timedelta(minutes=5)
    check_per_round = 5
    check_delta = round_delta / (check_per_round + 1)
    for round_index in range(10):
        time = begin_time + round_index * round_delta
        rounds = []
        for team_camps in camps:
            rounds.append([])
            for camp in team_camps:
                round = TeamCampRound(camp = camp, flag=str(uuid.uuid4()), begin_time=time, end_time=time+round_delta, index=round_index+1)
                session.add(round)
                rounds[-1].append(round)

                source_team_index = random.randint(0, 2 * len(groups))
                if source_team_index < len(groups):
                    group = groups[source_team_index]
                    submit = FlagSubmit(group=group, round=round, content=round.flag, submit_time=time+timedelta(seconds=random.randint(0, 120)))
                else:
                    group = random.choice(groups)
                    submit = FlagSubmit(group=group, round=None, content=str(uuid.uuid4()), submit_time=time+timedelta(seconds=random.randint(0, 120)))
                session.add(submit)

        for i in range(5):
            check_time = time + i * check_delta
            end_time = check_time + check_delta
            for camp_rounds in rounds:
                for round in camp_rounds:
                    state = random.choice(TeamServiceState.names)
                    log = TeamServiceCheckLog(round=round, state=state, trigger_time=check_time, finish_time=end_time, detail='for test')
                    session.add(log)






