from datetime import timedelta, datetime
from voip_shifts.bot import bot
from rq.job import get_current_job
from sqlalchemy import and_, select
from tzlocal import get_localzone

import subprocess

from voip_shifts.models import *
from voip_shifts.config import config, mode, log, session, rq



class Shifts():
    def __init__(self, employee_id:str, client_id:str, service_id:str, 
                start_date:datetime, end_date:datetime, minutes_time_delta:int, 
                active:bool, skip:bool) -> None:
        if mode == "prod":
            self.sip_server = config.SIP_SERVER
            self.password = config.SIP_PASSWORD
            self.number = config.SIP_NUMBER
            self.username = config.SIP_USERNAME
        self.client_id = client_id
        self.employee_id = employee_id
        self.service_id = service_id
        self.minutes_time_delta = minutes_time_delta
        self.start_date = start_date - timedelta(minutes=self.minutes_time_delta)
        self.end_date = end_date - timedelta(minutes=self.minutes_time_delta)
        self.active = active
        self.skip = skip
        self.on_shift_call = f"1+++++++{self.client_id}+++++"
        self.off_shift_call = f"2+++++++{self.client_id}+++++{self.service_id}+++++++1+++0+++++"

    def is_callable(self, datetime_:datetime) -> bool:
        if datetime.now(get_localzone()) < datetime_ + timedelta(minutes=10):
            return True
        return False

    def get_printable_time(self, date_time:datetime) -> str:
        return date_time.strftime("%m_%d_%y_%I:%M_%p")

    def shift_call(self, type_of_call) -> None:

        datetime_ = self.start_date if type_of_call is self.on_shift_call else self.end_date
        if not self.is_callable(datetime_):
            msg = f"""<b>Emploee {self.employee_id} shift call with {self.client_id}, \
                       service:{self.service_id} at {datetime_} UTC will not be executed \
                       {datetime.utcnow().strftime('%m-%d-%y-%I:%M')}</b>"""
            log.info(msg)
            bot.send_messages(msg)
            return None

        if mode == "prod":
            subprocess.run(
                [
                    "./call-prog",
                    "-r",
                    self.sip_server,
                    "-u",
                    self.username,
                    "-p",
                    self.password,
                    "-n",
                    self.number,
                    "-t",
                    "18558442600@" + self.sip_server,
                    "-d",
                    f"+4++++++{self.employee_id}++++++++2++++++{type_of_call}",
                    "-T",
                    f"{self.get_printable_time(datetime_)}_{self.client_id}",
                    "-P",
                    "9001",
                ]
            )
        msg = f"""Employee {self.employee_id} is {'On shift Call' if type_of_call is self.on_shift_call else 'Off shift call'}
            with {self.client_id}, service:{self.service_id} at {datetime.utcnow()} UTC0"""
        bot.send_messages(msg)
        log.info(f"Shift call executed {get_current_job().id}")
        timetable = session.scalar(
            select(TimetableModel).filter(
                TimetableModel.job_id==get_current_job().id
            )
        )
        daily_report = session.scalar(
            select(DailyReportModel).filter(and_(
                DailyReportModel.company_id==timetable.company_id,
                DailyReportModel.date==datetime_.date()
            ))
        )

        if daily_report is None:
            daily_report = DailyReportModel(
                call_count = 0,
                date = datetime_.date(),
                company_id = timetable.company,
            )
            session.add(daily_report)
            session.flush()
        daily_report.call_count += 1

        if type_of_call is self.on_shift_call:
            job = rq.enqueue_at(
                self.end_date + (datetime.now(get_localzone()) - self.start_date),
                self.shift_call,
                self.off_shift_call
            )
            log.info(f"Off shift call is in queue with {job.id}")
            timetable.job_id = job.id

        try:
            session.commit()
        except Exception as e:
            log.error(f"Commit don't exist. Exception is {e}")
            session.rollback()
        else:
            log.info(f"Off shift call job id is record with {job.id}")
        finally:
            session.close()
