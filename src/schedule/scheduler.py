from apscheduler.schedulers.background import BlockingScheduler

from src.schedule.disk_schedule import clear_files
from src.schedule.kono_tianmao_schedule import run_kono_tianmao
from src.schedule.kono_wph_schedule import get_and_upload_rank_data


def _kono_tianmao_schedule():
    run_kono_tianmao()

def _kono_wph_schedule():
    get_and_upload_rank_data()


def create_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler()

    # 每天凌晨清空磁盘缓存
    scheduler.add_job(clear_files, 'cron', hour=0, minute=0, second=0)

    # 每小时整点运行（排除 0 点）
    scheduler.add_job(
        _kono_tianmao_schedule,
        'cron',
        hour='1-23',  # 从1点到23点
        minute=0,
        second=0,
        misfire_grace_time=300
    )

    # 每天晚上 23:55 额外跑一次
    scheduler.add_job(
        _kono_tianmao_schedule,
        'cron',
        hour=23,
        minute=55,
        second=0,
        misfire_grace_time=300
    )

    # 每天早上8.30跑唯品会的排名
    scheduler.add_job(
        _kono_wph_schedule,
        'cron',
        hour=8,
        minute=30,
        second=0,
        misfire_grace_time=300
    )

    return scheduler


def create_scheduler_and_start():
    create_scheduler().start()


if __name__ == '__main__':
    create_scheduler_and_start()
