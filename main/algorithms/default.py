from django.db.models import Q
from django.utils import timezone

from ..models import *

from time import time, mktime, strftime, strptime, localtime
from datetime import date, datetime, timedelta

import logging


def get_delta_units_from_last_zero(appointed_datetime=timezone.now()):
    last_zero = datetime(
        year=appointed_datetime.year,
        month=appointed_datetime.month,
        day=appointed_datetime.day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )
    last_zero_delta = appointed_datetime - last_zero
    index = 0
    while last_zero_delta > UNITS[index]:
        index = index + 1
    logging.debug('next_unit_index: %d' % index)
    return UNIT * index


def get_next_workday(appointed_datetime=timezone.now()):
    next_workday = None
    for calendar_object in Calendar.objects.filter(date__gte=appointed_datetime)[:30]:
        if not calendar_object.is_holiday:
            next_workday = datetime(
                year=calendar_object.date.year,
                month=calendar_object.date.month,
                day=calendar_object.date.day,
                tzinfo = LOCAL_TIME_ZONE_INFO,
            )
            break

    logging.debug('next_workday after %s (include today): %s' % (appointed_datetime, next_workday))
    return next_workday


def get_next_unit(appointed_datetime=timezone.now()):
    next_workday = get_next_workday(appointed_datetime)

    next_unit = None
    if next_workday < appointed_datetime: # next workday is today
        delta_units_from_last_zero = get_delta_units_from_last_zero(appointed_datetime)
        next_unit = next_workday + delta_units_from_last_zero
    else:
        next_unit = next_workday
    return next_unit


def add_done_task_objects(user, serie_task_objects):
    pass


def get_actual_cost(start, cost, status):
    last_zero = datetime(
        year=timezone.now().year,
        month=timezone.now().month,
        day=timezone.now().day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )
    delta_units_from_last_zero = get_delta_units_from_last_zero()

    actual_cost = timedelta()
    if status == 'Doing':
        actual_cost = last_zero + delta_units_from_last_zero - start
    logging.debug('actual_cost: %s' % actual_cost)

    net_cost = UNIT * cost
    if status == 'Doing':
        calendar_objects = list(Calendar.objects
            .filter(date__gte=start)
            .filter(date__lt=last_zero)
        )
        logging.debug('Doing days: %s' % calendar_objects)
        for calendar_object in calendar_objects:
            if not calendar_object.is_holiday:
                net_cost = net_cost - ONE_DAY
        net_cost = net_cost - delta_units_from_last_zero
    logging.debug('net_cost: %s' % net_cost)

    loop_number = 0
    while net_cost > timedelta():
        loop_number = loop_number + 1
        logging.debug('loop_number: %d' % loop_number)
        if loop_number > 10:
            raise ValueError('Infinite Loop!')

        fetch_from_date = start + actual_cost + timedelta(days=1)
        for calendar_object in Calendar.objects.filter(date__gte=fetch_from_date)[:30]:

            if calendar_object.is_holiday:
                logging.debug('%s is holiday.' % calendar_object.date)

                actual_cost = actual_cost + ONE_DAY
                logging.debug('actual_cost: %s' % actual_cost)

            else:
                logging.debug('%s is workday.' % calendar_object.date)
                
                if net_cost > ONE_DAY:
                
                    actual_cost = actual_cost + ONE_DAY
                    logging.debug('actual_cost: %s' % actual_cost)
                
                    net_cost = net_cost - ONE_DAY
                    logging.debug('net_cost: %s' % net_cost)
                
                else:

                    actual_cost = actual_cost + net_cost
                    logging.debug('actual_cost: %s' % actual_cost)

                    net_cost = timedelta()
                    logging.debug('net_cost: %s' % net_cost)

                    break

    return actual_cost


def new_serie_task_object(user_cur, task_object):
    logging.debug(task_object)
    serie_task_object = {'task': task_object}

    start = user_cur
    if task_object.start is not None:
        start = task_object.start
        # TODO if the start day is holiday
    logging.debug('start: %s' % start)
    serie_task_object['start'] = start

    actual_cost = get_actual_cost(start, task_object.cost, STATUS_CHOICE_LIST[task_object.status])
    logging.debug('actual_cost: %s' % actual_cost)

    end = start + actual_cost
    logging.debug('end: %s' % end)
    serie_task_object['end'] = end
    if end > user_cur:
        user_cur = end
        logging.debug('user_cur: %s' % user_cur)
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

    task_objects = list(Task.objects
        .filter(~Q(start=None))
        .filter(assignee=user)
        .filter(status=STATUS_CHOICE_LIST.index('Todo'))
        .order_by('start')
    )
    for task_object in task_objects:
        user_starts.append(timezone.localtime(task_object.start, timezone=LOCAL_TIME_ZONE_INFO))

    user_starts.sort()
    return user_starts


def get_ready_todo_task_objects(todo_task_objects, taskposition_objects):
    ready_todo_task_objects = []
    ready_todo_task_objects_str_list = []
    for task_object in todo_task_objects:
        for taskposition_object in taskposition_objects:
            if task_object == taskposition_object.post:
                break
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
    logging.debug('user_starts: %s' % user_starts)

    todo_task_objects = list(Task.objects
        .filter(assignee=user)
        .filter(status=STATUS_CHOICE_LIST.index('Todo'))
        .order_by('-priority')
    )
    taskposition_objects = list(TaskPosition.objects
        .filter(pre__status=STATUS_CHOICE_LIST.index('Todo'))
    )

    while todo_task_objects:
        logging.debug('user_cur: %s' % user_cur)

        ready_todo_task_objects = get_ready_todo_task_objects(todo_task_objects, taskposition_objects)
        if not ready_todo_task_objects:
            raise RuntimeError('Toposorting failed! No task objects ready todo!')

        choose = None
        if len(user_starts) == 0:
            choose = task_object
        else:
            for task_object in ready_todo_task_objects:
                if task_object.start is not None and task_object.start == user_starts[0]:
                    choose = task_object
                    break
            if user_starts[0] != user_cur:
                for task_object in ready_todo_task_objects:
                    if task_object.start is None and (user_cur + UNIT * task_object.cost) <= user_starts[0]:
                        choose = task_object
                        break

        logging.info('Choose %s.' % choose)
        if choose is None:
            raise ValueError('Cannot continue!')

        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)

        if task_object.start is not None:
            user_starts.remove(task_object.start)
            logging.debug('user_starts: %s' % user_starts)
        
        serie_task_objects.append(serie_task_object)

        todo_task_objects.remove(task_object)
        remove_task_object_from_taskposition_objects(task_object, taskposition_objects)


def delete_old_serie_object(user):
    Serie.objects.filter(task__assignee=user).delete()


def save_new_serie_object(serie_task_objects):
    for serie_task_object in serie_task_objects:
        serie_object = Serie(
            task = serie_task_object['task'],
            start = serie_task_object['start'],
            end = serie_task_object['end'],
        )
        serie_object.save()


def refresh_serie_objects(user):
    logging.info('Refreshing serie objects...')
    tic = time()

    serie_task_objects = []
    user_cur = get_next_unit()
    add_done_task_objects(user, serie_task_objects)
    add_doing_task_objects(user, user_cur, serie_task_objects)
    add_todo_task_objects(user, user_cur, serie_task_objects)
    delete_old_serie_object(user)
    save_new_serie_object(serie_task_objects)

    toc = time()
    tictoc = toc - tic
    logging.debug('TicToc: %.3fs' % tictoc)
    logging.info('Refreshing serie objects...done.')
    return True
