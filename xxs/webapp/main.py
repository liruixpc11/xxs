# coding=UTF-8

import web
import json

from sqlalchemy import and_, func
from sqlalchemy.orm import scoped_session, sessionmaker

from xxs.models import *

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
            result.append(u'{} attack {} on {}'.format(flag.group.name, flag.round.camp.execution.group.name,
                                                       flag.round.camp.desc.name))
        return json.dumps(result)


class FlagList(object):
    def GET(self):
        web.header('Content-Type', 'application/json')

        input_data = web.input()
        task_id = input_data.task_id

        camp_names = [camp.name for camp in web.ctx.orm.query(CampDesc).order_by(CampDesc.name.asc()).all()]
        group_names = [execution.group.name for execution in web.ctx.orm.query(Execution).join(Group).filter(Execution.task_id==task_id).order_by(Group.name.asc()).all()]

        round_index = web.ctx.orm.query(func.max(TeamCampRound.index)).scalar()
        round_camps = web.ctx.orm.query(TeamCampRound).filter(TeamCampRound.index == round_index).all()
        data = []
        for round_camp in round_camps:
            if len(round_camp.submits) > 0:
                state = 'Attacked'
            else:
                last_log = web.ctx.orm.query(TeamServiceCheckLog).join(TeamCampRound).filter(
                    TeamCampRound.camp_id == round_camp.camp_id).order_by(TeamServiceCheckLog.trigger_time.desc()).first()
                if last_log:
                    state = last_log.state
                else:
                    state = TeamServiceState.Unknown

            data.append({
                "group_name": round_camp.camp.execution.group.name,
                "camp_name": round_camp.camp.desc.name,
                "status": state
            })

        result = {
            'camps': camp_names,
            'groups': group_names,
            'data': data
        }
        return json.dumps(result)


if __name__ == '__main__':
    db_factory.init_schema()
    app.run()
