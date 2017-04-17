# coding=UTF-8

import web
import json

from sqlalchemy import and_, func
from sqlalchemy.orm import scoped_session, sessionmaker

from xxs.models import *
from dba import *

urls = (
    "/pwn_data", "Pwn",
    "/flag_data", "FlagList"
)

db_factory = DbFactory()


def load_sqla(handler):
    web.ctx.orm = scoped_session(db_factory.make_session)
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()


app = web.application(urls, locals())
app.add_processor(load_sqla)


class Pwn(object):
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')

        input_data = web.input()
        last_id = int(input_data.last_id)
        task_id = input_data.task_id

        flags = web.ctx.orm.query(FlagSubmit).join(TeamCampRound).join(TeamCamp).join(Execution).join(Task).filter(and_(
            FlagSubmit.round != None,
            FlagSubmit.id > last_id,
            Task.id == task_id
        )).order_by(FlagSubmit.id.asc()).all()

        result = []
        for flag in flags:
            result.append({
                'attacker_name': flag.group.name,
                'attacker_logo': flag.group.logo_url,
                'victim_name': flag.round.camp.execution.group.name,
                'victim_logo': flag.round.camp.execution.group.logo_url,
                'camp_name': flag.round.camp.desc.name,
                'timestamp': flag.submit_time.strftime('%Y-%m-%d %H:%M:%S'),
                'round_index': flag.round.index
            })

        return json.dumps(result)


class FlagList(object):
    def GET(self):
        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', '*')

        input_data = web.input()
        task_id = input_data.task_id

        camp_names = [camp.name for camp in web.ctx.orm.query(CampDesc).order_by(CampDesc.name.asc()).all()]
        groups = [{"name": execution.group.name, "logo": execution.group.logo_url} for execution in
                       web.ctx.orm.query(Execution).join(Group).filter(Execution.task_id == task_id).order_by(
                           Group.name.asc()).all()]
        group_names = [group['name'] for group in groups]

        round_index, round_camps = query_current_rounds(web.ctx.orm, task_id)
        data = []
        for round_camp in round_camps:
            last_log = web.ctx.orm.query(TeamServiceCheckLog).join(TeamCampRound).filter(
                TeamCampRound.camp_id == round_camp.camp_id).order_by(TeamServiceCheckLog.trigger_time.desc()).first()
            if last_log:
                service_state = last_log.state
            else:
                service_state = TeamServiceState.Unknown

            attacked = len(round_camp.submits) > 0
            if attacked:
                attack_state = 'Attacked'
                if service_state == TeamServiceState.Blocked:
                    state = 'Attacked&Blocked'
                else:
                    state = 'Attacked'
            else:
                attack_state = 'Normal'
                state = service_state

            data.append({
                "group_name": round_camp.camp.execution.group.name,
                "camp_name": round_camp.camp.desc.name,
                "status": state,
                "attack_status": attack_state,
                "service_status": service_state
            })

        round_scores = calc_scores_for_rounds(round_camps)
        total_scores = calc_scores(web.ctx.orm, task_id)
        last_submits = query_last_submits(web.ctx.orm, task_id)

        result = {
            'camps': camp_names,
            'groups': groups,
            'group_names': group_names,
            'data': data,
            'round_scores': round_scores,
            'total_scores': total_scores,
            'round_index': round_index,
            'last_submits': last_submits,
            'lastsubmit': map(lambda s: group_names.index(s) + 1, last_submits),
            'points': total_scores
        }

        return json.dumps(result)


if __name__ == '__main__':
    db_factory.init_schema()
    app.run()
