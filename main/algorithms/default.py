from django.db.models import Q

from ..models import *

import logging
import time, datetime


def init_logger():
    time_str = time.strftime('%Y%m%d_%H%M%S', time.localtime())

    logger = logging.getLogger()
    format = '%(asctime)s %(levelname)s %(lineno)d %(message)s'
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(format))
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)

    # fh = logging.FileHandler('%s.log' % time_str)
    # fh.setFormatter(logging.Formatter(format))
    # fh.setLevel(logging.DEBUG)
    # logger.addHandler(fh)


def next_workday(appointed_date=TOMORROW):
    for calendar_object in Calendar.objects.filter(date__gte=appointed_date)[:30]:
        if not calendar_object.is_holiday:
            logging.debug('next_workday: %s' % calendar_object.date)
            return calendar_object.date

    # TODO
    return appointed_date


def compute_actual_cost(start, cost):
    actual_cost = 0
    net_cost = UNIT * cost
    logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))
    logging.debug('net_cost: %.1f days' % (net_cost / ONE_DAY_TIMESTAMP))

    if abs(start - TODAY_TIMESTAMP) % ONE_DAY_TIMESTAMP == 0:
        logging.debug('At zero.')
    else:
        logging.debug('Not at zero.')
        start_day_rest = abs(start - TODAY_TIMESTAMP) % ONE_DAY_TIMESTAMP
        net_cost = net_cost - start_day_rest
        actual_cost = actual_cost + start_day_rest
        logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))
        logging.debug('net_cost: %.1f days' % (net_cost / ONE_DAY_TIMESTAMP))

    loop_number = 0
    while net_cost > 0:
        loop_number = loop_number + 1
        logging.debug('loop_number: %d' % loop_number)
        if loop_number > 10:
            raise ValueError('Infinite Loop!')

        appointed_date = convert_timestamp_to_date(start + actual_cost)
        logging.debug('appointed_date: %s' % appointed_date)
        
        fetch_days_count = net_cost // ONE_DAY_TIMESTAMP + 1
        logging.debug('fetch_days_count: %d' % fetch_days_count)

        fetch_days = Calendar.objects.filter(date__gte=appointed_date)[:fetch_days_count]
        for calendar_object in fetch_days:

            if calendar_object.is_holiday:
                logging.debug('%s is holiday.' % calendar_object.date)
                actual_cost = actual_cost + ONE_DAY_TIMESTAMP
                logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))
                logging.debug('net_cost: %.1f days' % (net_cost / ONE_DAY_TIMESTAMP))

            else:
                logging.debug('%s is workday.' % calendar_object.date)
                if net_cost > ONE_DAY_TIMESTAMP:
                    actual_cost = actual_cost + ONE_DAY_TIMESTAMP
                    net_cost = net_cost - ONE_DAY_TIMESTAMP
                    logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))
                    logging.debug('net_cost: %.1f days' % (net_cost / ONE_DAY_TIMESTAMP))
                else:
                    actual_cost = actual_cost + net_cost
                    net_cost = 0
                    logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))
                    logging.debug('net_cost: %.1f days' % (net_cost / ONE_DAY_TIMESTAMP))
                    break

    return actual_cost


def new_serie_task_object(user_cur, task_object):
    logging.debug(task_object)
    serie_task_object = {'task': task_object}

    start = user_cur
    if task_object.start is not None:
        start = convert_date_to_timestamp(task_object.start)
        # TODO if the start day is holiday
    logging.debug('start: %s' % convert_timestamp_to_date_yyyy_mm_dd(start))
    serie_task_object['start'] = start

    actual_cost = compute_actual_cost(start, task_object.cost)
    logging.debug('actual_cost: %.1f days' % (actual_cost / ONE_DAY_TIMESTAMP))

    end = start + actual_cost
    logging.debug('end: %s' % convert_timestamp_to_date_yyyy_mm_dd(end))
    serie_task_object['end'] = end
    if end > user_cur:
        user_cur = serie_task_object['end']
        logging.debug('user_cur: %s' % convert_timestamp_to_date_yyyy_mm_dd(user_cur))
    else:
        pass
        # TODO warning

    logging.debug('serie_task_object: %s' % serie_task_object)
    return user_cur, serie_task_object


def add_doing_task_objects(user, user_cur, serie_task_objects):
    doing_task_objects = list(
        Task.objects.filter(assignee=user)
                    .filter(status=STATUS_CHOICE_LIST.index('Doing'))
                    .order_by('id')
    )
    for task_object in doing_task_objects:
        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)
        serie_task_objects.append(serie_task_object)


def get_user_starts(user):
    user_starts = []

    task_objects = list(
        Task.objects.filter(~Q(start=None))
                    .filter(assignee=user)
                    .filter(status=STATUS_CHOICE_LIST.index('Todo'))
                    .order_by('start')
    )
    for task_object in task_objects:
        start = convert_date_to_timestamp(task_object.start)
        user_starts.append(start)

    user_starts.sort()
    return user_starts


def logging_user_starts(user_starts):
    user_starts_str_list = []
    for user_start in user_starts:
        user_starts_str_list.append(convert_timestamp_to_date_yyyy_mm_dd(user_start))
    logging.debug('user_starts_str_list: %s' % user_starts_str_list)


def get_ready_todo_task_objects(todo_task_objects, taskposition_objects):
    ready_todo_task_objects = []
    ready_todo_task_objects_str_list = []
    for task_object in todo_task_objects:
        for taskposition_object in taskposition_objects:
            if task_object == taskposition_object.post:
                continue
        else:
            ready_todo_task_objects.append(task_object)
            ready_todo_task_objects_str_list.append(str(task_object))

    logging.debug('ready_todo_task_objects: %s' % ready_todo_task_objects_str_list)
    return ready_todo_task_objects


def remove_task_object_from_taskposition_objects(task_object, taskposition_objects):
    to_remove = []
    for taskposition_object in taskposition_objects:
        if task_object == taskposition_object.pre or task_object == taskposition_object.post:
            to_remove.append(taskposition_object)
    for taskposition_object in to_remove:
        taskposition_objects.remove(taskposition_object)


def add_todo_task_objects(user, user_cur, serie_task_objects):
    user_starts = get_user_starts(user)
    logging_user_starts(user_starts)

    todo_task_objects = list(
        Task.objects.filter(assignee=user)
                    .filter(status=STATUS_CHOICE_LIST.index('Todo'))
                    .order_by('-priority')
    )
    taskposition_objects = list(TaskPosition.objects.all())

    while todo_task_objects:
        ready_todo_task_objects = get_ready_todo_task_objects(todo_task_objects, taskposition_objects)
        if not ready_todo_task_objects:
            raise ValueError('Toposorting failed!')

        choose = None
        candicate = None
        for task_object in ready_todo_task_objects:

            if task_object.start is not None:
                candicate = task_object

            if len(user_starts) == 0:
                choose = task_object
                break
            else:
                user_cur_to_start = user_starts[0] - user_cur
                cost = UNIT * task_object.cost
                if user_cur_to_start < 0:
                    raise ValueError('???')
                elif user_cur_to_start < cost:
                    continue
                else:
                    choose = task_object
                    break

        else:
            choose = candicate

        logging.info('Choose %s.' % choose)
        if choose is None:
            raise ValueError('Cannot continue!')

        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)

        if task_object.start is not None:
            user_starts.remove(task_object.start)
            logging_user_starts(user_starts)
        
        serie_task_objects.append(serie_task_object)

        todo_task_objects.remove(task_object)
        remove_task_object_from_taskposition_objects(task_object, taskposition_objects)


def delete_old_serie_object(user):
    for serie_object in Serie.objects.all():
        if serie_object.task.assignee == user:
            serie_object.delete()


def save_new_serie_object(serie_task_objects):
    for serie_task_object in serie_task_objects:
        serie_object = Serie(
            task = serie_task_object['task'],
            start = serie_task_object['start'],
            end = serie_task_object['end'],
        )
        serie_object.save()


def refresh_serie_objects(user):
    init_logger()
    logging.info('Refreshing serie objects...')

    tic = time.time()

    user_cur = convert_date_to_timestamp(next_workday())

    serie_task_objects = []

    add_doing_task_objects(user, user_cur, serie_task_objects)
    add_todo_task_objects(user, user_cur, serie_task_objects)

    delete_old_serie_object(user)
    save_new_serie_object(serie_task_objects)

    toc = time.time()
    tictoc = toc - tic
    logging.debug('TicToc: %.3fs' % tictoc)

    logging.info('Refreshing serie objects...done.')
    return True
