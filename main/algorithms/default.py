from django.db.models import Q

from ..models import *



def new_serie_task_object(user_cur, task_object):
    serie_task_object = {'task': task_object}

    username = task_object.assignee.username

    start = user_cur[username]
    if task_object.start is not None:
        start = convert_date_to_timestamp(task_object.start)
    serie_task_object['start'] = start

    end = start + UNIT * task_object.cost
    serie_task_object['end'] = end
    if end > user_cur[username]:
        user_cur[username] = serie_task_object['end']
    else:
        pass
        # TODO warning

    return user_cur, serie_task_object


def add_doing_task_objects(user_cur, serie_task_objects):
    doing_task_objects = list(
        Task.objects.filter(~Q(assignee=None))
                    .filter(status=STATUS_CHOICE_LIST.index('Doing'))
                    .order_by('id')
    )
    for task_object in doing_task_objects:
        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)
        serie_task_objects.append(serie_task_object)


def get_user_starts():
    user_starts = {}
    for user_object in User.objects.all():
        user_starts[user_object.username] = []

    task_objects = list(
        Task.objects.filter(~Q(start=None))
                    .filter(~Q(assignee=None))
                    .filter(status=STATUS_CHOICE_LIST.index('Todo'))
                    .order_by('start')
    )
    for task_object in task_objects:
        start = convert_date_to_timestamp(task_object.start)
        username = task_object.assignee.username
        user_starts[username].append(start)

    for username, starts in user_starts.items():
        starts.sort()

    return user_starts


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


def add_todo_task_objects(user_cur, serie_task_objects):
    user_starts = get_user_starts()

    todo_task_objects = list(
        Task.objects.filter(~Q(assignee=None))
                    .filter(status=STATUS_CHOICE_LIST.index('Todo'))
                    .order_by('-priority')
    )
    taskposition_objects = list(TaskPosition.objects.all())

    while todo_task_objects:
        ready_todo_task_objects = get_ready_todo_task_objects(todo_task_objects, taskposition_objects)
        if not ready_todo_task_objects:
            raise ValueError('Toposorting is failed!')

        choose = None
        candicate = None
        for task_object in ready_todo_task_objects:
            username = task_object.assignee.username

            if task_object.start is not None:
                candicate = task_object

            if len(user_starts[username]) == 0:
                choose = task_object
                break
            else:
                user_cur_to_start = user_starts[username][0] - user_cur[username]
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

        if choose is None:
            raise ValueError('Cannot continue!')

        user_cur, serie_task_object = new_serie_task_object(user_cur, task_object)

        if task_object.start is not None:
            user_starts[username].remove(user_cur[username])
        
        serie_task_objects.append(serie_task_object)

        todo_task_objects.remove(task_object)
        remove_task_object_from_taskposition_objects(task_object, taskposition_objects)


def save_serie_object(serie_task_objects):
    Serie.objects.all().delete()

    for serie_task_object in serie_task_objects:
        serie_object = Serie(
            task = serie_task_object['task'],
            start = serie_task_object['start'],
            end = serie_task_object['end'],
        )
        serie_object.save()


def refresh_serie_objects():
    tic = time.time()

    user_cur = {}
    for user_object in User.objects.all():
        user_cur[user_object.username] = TODAY

    serie_task_objects = []

    add_doing_task_objects(user_cur, serie_task_objects)
    # add_should_be_doing_task_objects(user_cur, serie_task_objects)
    add_todo_task_objects(user_cur, serie_task_objects)
    
    save_serie_object(serie_task_objects)

    toc = time.time()
    tictoc = toc - tic
    print('Refreshing serie objects cost %.3fs.' % tictoc)
    return True
