from django.db.models import Q

from .models import *

import datetime, time


day = 1000 * 60 * 60 * 24
unit = day // 2 # TODO


def convert_date_to_timestamp(date):
    return 1000 * int(time.mktime(date.timetuple()))


today = convert_date_to_timestamp(datetime.date.today())


def add_doing_task_objects(user_cur, series_object_dict):
    doing_task_objects = Task.objects.filter(status=STATUS_CHOICE_LIST.index('doing')).order_by('id')
    for task_object in doing_task_objects:
        series_project_task_object = {
            'id': str(task_object.id),
            'name': str(task_object),
        }

        user = 'nobody'
        if task_object.assignee is not None:
            user = task_object.assignee.name
            series_project_task_object['owner'] = user

        start = convert_date_to_timestamp(task_object.start)
        series_project_task_object['start'] = start

        end = start + unit * task_object.cost
        if end > today:
            series_project_task_object['end'] = end
            if end > user_cur[user]:
                user_cur[user] = series_project_task_object['end']
        else:
            series_project_task_object['end'] = today
            # TODO warning

        if task_object.project is not None:
            series_object_dict[task_object.project.name]['data'].append(series_project_task_object)


def get_user_starts(user_starts):
    task_objects = list(Task.objects.filter(status=STATUS_CHOICE_LIST.index('todo')).filter(~Q(start=None)).order_by('start'))
    for task_object in task_objects:
        start = convert_date_to_timestamp(task_object.start)

        user = 'nobody'
        if task_object.assignee is not None:
            user = task_object.assignee.name

        user_starts[user].append(start)

    for user, starts in user_starts.items():
        starts.sort()


def get_ready_todo_task_objects(todo_task_objects, taskposition_objects):
    ready_todo_task_objects = []
    for task_object in todo_task_objects:
        for taskposition_object in taskposition_objects:
            if task_object == taskposition_object.post:
                continue
        else:
            ready_todo_task_objects.append(task_object)
    return ready_todo_task_objects


def remove_task_object_from_taskposition_objects(task_object, taskposition_objects):
    to_remove = []
    for taskposition_object in taskposition_objects:
        if task_object == taskposition_object.pre or task_object == taskposition_object.post:
            to_remove.append(taskposition_object)
    for taskposition_object in to_remove:
        taskposition_objects.remove(taskposition_object)


def add_todo_task_objects(user_cur, user_starts, series_object_dict):
    get_user_starts(user_starts)

    todo_task_objects = list(Task.objects.filter(status=STATUS_CHOICE_LIST.index('todo')).order_by('-priority'))
    taskposition_objects = list(TaskPosition.objects.all())

    while todo_task_objects:
        ready_todo_task_objects = get_ready_todo_task_objects(todo_task_objects, taskposition_objects)
        if not ready_todo_task_objects:
            raise ValueError('Toposorting is failed!')

        choose = None
        candicate = None
        for task_object in ready_todo_task_objects:
            user = 'nobody'
            if task_object.assignee is not None:
                user = task_object.assignee.name

            if task_object.start is not None:
                candicate = task_object

            if len(user_starts[user]) == 0:
                choose = task_object
                break
            else:
                user_cur_to_start = user_starts[user][0] - user_cur[user]
                cost =  unit * task_object.cost
                if user_cur_to_start < 0:
                    raise ValueError('???')
                elif user_cur_to_start < cost:
                    continue
                else:
                    choose = task_object
                    break

        else:
            choose = candicate

        if choose is None:
            raise ValueError('Cannot continue!')

        series_project_task_object = {
            'id': str(task_object.id),
            'name': str(task_object),
        }

        user = 'nobody'
        if task_object.assignee is not None:
            user = task_object.assignee.name
            series_project_task_object['owner'] = user

        start = user_cur[user]
        if task_object.start is not None:
            start = convert_date_to_timestamp(task_object.start)
            user_cur[user] = start
            user_starts[user].remove(start)
        series_project_task_object['start'] = start

        end = user_cur[user] + unit * task_object.cost
        user_cur[user] = end
        series_project_task_object['end'] = end
        
        if task_object.project is not None:
            series_object_dict[task_object.project.name]['data'].append(series_project_task_object)

        todo_task_objects.remove(task_object)
        remove_task_object_from_taskposition_objects(task_object, taskposition_objects)


def get_series_object():
    tic = time.time()

    user_cur = {'nobody': today}
    user_starts = {'nobody': []}
    user_objects = User.objects.all()
    for user_object in user_objects:
        user_cur[user_object.name] = today
        user_starts[user_object.name] = []

    series_object_dict = {}
    project_objects = Project.objects.all()
    for project_object in project_objects:
        series_object_dict[project_object.name] = {
            'name': project_object.name,
            'data': [],
        }

    add_doing_task_objects(user_cur, series_object_dict)
    # add_should_be_doing_task_objects(user_cur, series_object_dict)
    add_todo_task_objects(user_cur, user_starts, series_object_dict)

    series_object_list = []
    for key, value in series_object_dict.items():
        series_object_list.append(value)

    toc = time.time()
    tictoc = toc - tic
    print('tictoc: %ss' % tictoc)
    return series_object_list
