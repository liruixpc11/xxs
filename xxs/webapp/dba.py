# coding=UTF-8

from collections import defaultdict
from sqlalchemy import and_, func
from xxs.models import *


def query_current_rounds(session, task_id):
    round_index = session.query(func.max(TeamCampRound.index)).join(TeamCamp).join(Execution).join(Task).filter(Task.id==task_id).scalar()
    camp_rounds = session.query(TeamCampRound).join(TeamCamp).join(Execution).join(Task).filter(and_(Task.id == task_id,
                                                                                                     TeamCampRound.index == round_index)).all()
    return round_index, camp_rounds


def calc_round_scores(session, task_id, round_index):
    camp_rounds = session.query(TeamCampRound).join(TeamCamp).join(Execution).join(Task).filter(and_(Task.id == task_id,
                                                                                       TeamCampRound.index == round_index)).all()
    return calc_scores_for_rounds(camp_rounds)


def calc_scores_for_rounds(camp_rounds):
    score_dict = defaultdict(int)
    for camp_round in camp_rounds:
        group_name = camp_round.camp.execution.group.name
        team_score, attacker_scores = camp_round.calc_score()
        score_dict[group_name] += team_score
        for name, score in attacker_scores.items():
            score_dict[name] += score

    return score_dict


def calc_scores(session, task_id):
    camp_rounds = session.query(TeamCampRound).join(TeamCamp).join(Execution).join(Task).filter(Task.id == task_id).all()
    return calc_scores_for_rounds(camp_rounds)


def query_last_submits(session, task_id):
    result = session.query(FlagSubmit, func.max(FlagSubmit.submit_time)).join(TeamCampRound).join(TeamCamp).join(Execution).join(Task).filter(Task.id == task_id).group_by(FlagSubmit.group_id).all()
    result = sorted(result, key=lambda r: r[1])
    return list(reversed(map(lambda r: r[0].group.name, result)))


if __name__ == '__main__':
    db_factory = DbFactory()
    with db_factory.create_session() as session:
        print query_last_submits(session, 1)
