from django.db.models import Q
from django.utils import timezone

from ..models import *

from time import time, mktime, strftime, strptime, localtime
from datetime import date, datetime, timedelta

import logging


def get_delta_units_from_last_zero(appointed_datetime=timezone.now(), flag='ceil'):
    appointed_datetime_local = appointed_datetime.astimezone(LOCAL_TIME_ZONE_INFO)
    logging.debug('appointed_datetime_local: %s' % appointed_datetime_local)

    last_zero = datetime(
        year=appointed_datetime_local.year,
        month=appointed_datetime_local.month,
        day=appointed_datetime_local.day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )
    last_zero_delta = appointed_datetime_local - last_zero
    logging.debug('last_zero_delta: %s' % last_zero_delta)

    index = 0
    while last_zero_delta > UNITS[index]:
        logging.debug('index: %d' % index)
        index = index + 1
    logging.debug('next_unit_index: %d' % index)

    delta_units_from_last_zero = UNIT * (index - 1)
    if flag == 'floor':
        delta_units_from_last_zero = UNIT * index
    
    logging.debug('delta_units_from_last_zero to %s\'s %s: %s' % (appointed_datetime_local, flag, delta_units_from_last_zero))
    return delta_units_from_last_zero


def get_next_workday(appointed_datetime=timezone.now()):
    appointed_datetime_local = appointed_datetime.astimezone(LOCAL_TIME_ZONE_INFO)
    logging.debug('appointed_datetime_local: %s' % appointed_datetime_local)

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

    logging.debug('next_workday after %s (include today): %s' % (appointed_datetime_local, next_workday))
    return next_workday


def get_next_unit(appointed_datetime=timezone.now()):
    next_workday = get_next_workday(appointed_datetime)

    next_unit = None
    if next_workday < appointed_datetime: # next workday is today
        next_unit = next_workday + get_delta_units_from_last_zero(appointed_datetime, flag='floor')
    else:
        next_unit = next_workday

    return next_unit


def add_done_task_objects(user, serie_task_objects):
    return serie_task_objects


def get_actual_cost(start, cost, status_str):
    now_local = timezone.now().astimezone(LOCAL_TIME_ZONE_INFO)
    last_zero = datetime(
        year=now_local.year,
        month=now_local.month,
        day=now_local.day,
        tzinfo=LOCAL_TIME_ZONE_INFO,
    )
    actual_cost = timedelta()
    if status_str == 'Doing':
        actual_cost = last_zero + get_delta_units_from_last_zero(flag='floor') - start
    logging.debug('actual_cost: %s' % actual_cost)

    net_cost = UNIT * cost
    logging.debug('net_cost: %s' % net_cost)
    if status_str == 'Doing':
        calendar_objects = list(Calendar.objects
            .filter(date__gte=start)
            .filter(date__lte=last_zero)
        )

        # start
        start_delta_units = get_delta_units_from_last_zero(appointed_datetime=start, flag='floor')
        net_cost = net_cost + start_delta_units - ONE_DAY
        logging.debug('net_cost: %s' % net_cost)

        # middle
        for calendar_object in calendar_objects[1:-1]:
            if not calendar_object.is_holiday:
                net_cost = net_cost - ONE_DAY
                logging.debug('net_cost: %s' % net_cost)
        
        # end = now
        end_delta_units = get_delta_units_from_last_zero(flag='floor')
        if len(calendar_objects) == 1:
            net_cost = net_cost + ONE_DAY - end_delta_units
        else:
            net_cost = net_cost - end_delta_units
        logging.debug('net_cost: %s' % net_cost)

    loop_number = 0
    while net_cost > timedelta():
        loop_number = loop_number + 1
        logging.debug('loop_number: %d' % loop_number)
        if loop_number > 12:
            raise ValueError('Infinite Loop!')

        fetch_from_date = start + actual_cost
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
    logging.debug('new serie_task_object for %s' % task_object)
    serie_task_object = {'task': task_object}

    start = user_cur
    if task_object.start is not None:
        start = task_object.start
    logging.debug('start: %s' % start)
    serie_task_object['start'] = start

    actual_cost = get_actual_cost(start, task_object.cost, task_object.status_str)
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
    logging.debug('Add doing task objects...')
    doing_task_objects = list(
        Task.objects.filter(user=user)
                    .filter(status=STATUS_CHOICE_STR_LIST.index('Doing'))
                    .order_by('id')
    )
    for task_object in doing_task_objects:
        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)
        serie_task_objects.append(serie_task_object)

    logging.debug('Add doing task objects...done')
    return user_cur, serie_task_objects


def get_user_starts(user):
    user_starts = []

    task_objects = list(Task.objects
        .filter(~Q(start=None))
        .filter(user=user)
        .filter(status=STATUS_CHOICE_STR_LIST.index('Todo'))
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


def choose_ready_todo_task_object(ready_todo_task_objects, user_cur, user_starts):
    choice = None

    if len(user_starts) == 0:

        choice = ready_todo_task_objects[0]

    else:

        for task_object in ready_todo_task_objects:
            if task_object.start is not None and task_object.start == user_starts[0]:
                choice = task_object
                break

        if choice.start != user_cur:

            # try insterting a task before user_starts[0]
            for task_object in ready_todo_task_objects:
                if task_object.start is None:
                    actual_cost = get_actual_cost(user_cur, task_object.cost, task_object.status_str)
                    end = user_cur + actual_cost
                    if end < user_starts[0]:
                        choice = task_object
                        break

    return choice


def remove_task_object_from_taskposition_objects(task_object, taskposition_objects):
    to_remove = []
    for taskposition_object in taskposition_objects:
        if task_object == taskposition_object.pre or task_object == taskposition_object.post:
            to_remove.append(taskposition_object)
    for taskposition_object in to_remove:
        taskposition_objects.remove(taskposition_object)


def update_ref(choice, user_starts, todo_task_objects, taskposition_objects):
    if choice.start is not None:
        user_starts.remove(choice.start)
        logging.debug('user_starts: %s' % user_starts)

    todo_task_objects.remove(choice)
    remove_task_object_from_taskposition_objects(choice, taskposition_objects)


def add_todo_task_objects(user, user_cur, serie_task_objects):
    logging.debug('Add todo task objects...')

    user_cur = get_next_unit(appointed_datetime=user_cur)
    logging.debug('user_cur: %s' % user_cur)

    user_starts = get_user_starts(user)
    logging.debug('user_starts: %s' % user_starts)

    todo_task_objects = list(Task.objects
        .filter(user=user)
        .filter(status=STATUS_CHOICE_STR_LIST.index('Todo'))
        .order_by('-priority')
    )
    taskposition_objects = list(TaskPosition.objects
        .filter(pre__status=STATUS_CHOICE_STR_LIST.index('Todo'))
    )

    while todo_task_objects:
        logging.debug('user_cur: %s' % user_cur)

        ready_todo_task_objects = get_ready_todo_task_objects(todo_task_objects, taskposition_objects)
        if not ready_todo_task_objects:
            raise RuntimeError('Toposorting failed! No task objects ready todo!')

        choice = choose_ready_todo_task_object(ready_todo_task_objects, user_cur, user_starts)
        logging.info('Choose %s' % choice)
        if choice is None:
            raise ValueError('No choice!')

        user_cur, serie_task_object = new_serie_task_object(user_cur, choice)
        serie_task_objects.append(serie_task_object)
        
        update_ref(choice, user_starts, todo_task_objects, taskposition_objects)

    logging.debug('Add todo task objects...done')
    return user_cur, serie_task_objects


def delete_old_serie_object(user):
    Serie.objects.filter(task__user=user).delete()


def save_new_serie_object(serie_task_objects):
    for serie_task_object in serie_task_objects:
        serie_object = Serie(
            task = serie_task_object['task'],
            start = serie_task_object['start'],
            end = serie_task_object['end'],
        )
        serie_object.save()


def refresh_serie_objects(user):
    logging.info('Refreshing serie objects for %s...' % user)
    tic = time()

    serie_task_objects = []

    serie_task_objects = add_done_task_objects(user, serie_task_objects)

    user_cur = get_next_unit()
    logging.debug('user_cur: %s' % user_cur)
    
    user_cur, serie_task_objects = add_doing_task_objects(user, user_cur, serie_task_objects)
    logging.debug('user_cur: %s' % user_cur)
    logging.debug('serie_task_objects: %s' % serie_task_objects)

    user_cur, serie_task_objects = add_todo_task_objects(user, user_cur, serie_task_objects)
    logging.debug('user_cur: %s' % user_cur)
    logging.debug('serie_task_objects: %s' % serie_task_objects)

    delete_old_serie_object(user)
    save_new_serie_object(serie_task_objects)

    toc = time()
    tictoc = toc - tic
    logging.debug('TicToc: %.3fs' % tictoc)
    logging.info('Refreshing serie objects for %s...done.' % user)
    return True
