from infiniguard_api.lib.logging import iguard_logging
from sqlalchemy import (create_engine,
                        Column,
                        Integer,
                        String,
                        DateTime,
                        Float,
                        text,
                        ForeignKey
                        )
from sqlalchemy.sql.expression import insert, update, delete, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Query
from sqlalchemy.interfaces import PoolListener
from sqlalchemy.pool import SingletonThreadPool
import datetime
from infiniguard_api.lib.hw.threads import submit_sql, resultq
from time import sleep, time
from multiprocessing import Lock
log = iguard_logging.get_logger(__name__)
lock = Lock()


DBPATH = '/var/tmp/tasks.db'
MAX_TASKS = 1000  # Maximum number of tasks to keep
DELETE_CHUNK = 5000  # Number of rows to delete at each time

SELECT = 0  # Select queue
FOREGROUND = 1  # Foreground queue
BACKGROUND = 2  # Background queue


def timed(f):
    def wrapper(*args, **kwargs):
        start = time()
        res = f(*args, **kwargs)
        elapsed = time() - start
        log.debug('{:<20} took {:.3f} sec'.format(f.__name__, elapsed))
        return res
    return wrapper


class MyListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        dbapi_con.isolation_level = None
        dbapi_con.execute("pragma encoding = 'UTF-8'")
        dbapi_con.execute("PRAGMA journal_mode = wal")
        dbapi_con.execute("PRAGMA auto_vacuum = FULL")
        dbapi_con.execute('PRAGMA cache_size = -1000000')
        dbapi_con.execute('PRAGMA temp_store = MEMORY')
        dbapi_con.execute("PRAGMA foreign_keys=ON")


Base = declarative_base()
engine = create_engine('sqlite:///{}'.format(DBPATH),
                       echo=False,
                       isolation_level="READ UNCOMMITTED",
                       listeners=[MyListener()],
                       pool_size=50,
                       poolclass=SingletonThreadPool,
                       connect_args={'check_same_thread': False}
                       )


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True)
    rc = Column(Integer, nullable=True)
    stdout = Column(String, nullable=True)
    stderr = Column(String, nullable=True)
    status = Column(String, default='RUNNING')
    start = Column(DateTime, nullable=True)
    end = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    name = Column(String, nullable=True)
    command = Column(String, nullable=True)


class FileList(Base):
    __tablename__ = 'filelist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey(
        'tasks.task_id', ondelete="CASCADE"), index=True)
    filename = Column(String, nullable=True, index=True)
    ctime = Column(Integer, nullable=True, index=True)
    mtime = Column(Integer, nullable=True, index=True)
    mode = Column(Integer, nullable=True, index=True)
    size = Column(Integer, nullable=True, index=True)
    uid = Column(Integer, nullable=True, index=True)
    gid = Column(Integer, nullable=True, index=True)


class CommandOutput(Base):
    __tablename__ = 'cmdout'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey(
        'tasks.task_id', ondelete="CASCADE"), index=True)
    timestamp = Column(Integer, nullable=True, index=True)
    line = Column(String, nullable=True)
    stdstream = Column(Integer)


Base.metadata.create_all(engine)
session_factory = sessionmaker(bind=engine, autocommit=True)
Session = scoped_session(session_factory)


def get_session():
    return Session


@timed
def submit_select(statement):
    # Using lock to guarantee that the result of select is 
    # the one sent by submit_sql(statement)
    with lock:
        submit_sql(statement, priority=SELECT)
        return resultq.get()


@timed
def task_start(task_id, name, command):
    log.info('Starting task id:{} name:{} command:{}'.format(
        task_id, name, command))
    values = {
        'task_id': task_id,
        'start': datetime.datetime.utcnow(),
        'name': name,
        'command': command,
        'status': 'RUNNING'
    }
    statement = insert(Task).values(values)
    submit_sql(statement, priority=FOREGROUND)

    while True:
        statement = select([Task]).where(Task.task_id == task_id)
        task = submit_select(statement)
        if task:
            break
        sleep(0.01)

    delete_old_tasks()

    return task[0]


@timed
def task_end(task_id, task_start, rc, stdout, stderr):
    end = datetime.datetime.utcnow()
    values = {
        'end': end,
        'duration': (end - task_start).total_seconds(),
        'rc': rc,
        'stderr': stderr,
        'status': 'FINISHED',
        'stdout': stdout,
    }
    statement = update(Task).where(Task.task_id == task_id).values(values)
    submit_sql(statement, priority=BACKGROUND)


@timed
def task_update_files(task_id, filelist):
    if filelist:
        rows = list()
        for fileobj in filelist:
            filename, size, ctime, mtime, mode, uid, gid = fileobj
            row = {
                'filename': filename,
                'size': size,
                'ctime': ctime,
                'mtime': mtime,
                'mode': mode,
                'uid': uid,
                'gid': gid,
                'task_id': task_id
            }
            rows.append(row)

        statement = insert(FileList).values(rows)
        submit_sql(statement, priority=BACKGROUND)


@timed
def task_update_line(task_id, line, stdstream):
    def calculate_timestamp():
        epoch = datetime.datetime.utcfromtimestamp(0)
        now = datetime.datetime.utcnow()
        return int((now - epoch).total_seconds() * 1000)

    if line:
        log.debug(f'{line}')
        timestamp = calculate_timestamp()
        values = {
            'task_id': task_id,
            'timestamp': timestamp,
            'line': str(line),
            'stdstream': stdstream
        }
        statement = insert(CommandOutput).values(values)
        submit_sql(statement, priority=BACKGROUND)


@timed
def delete_task(task_id):
    log.info('Delete task id:{}'.format(task_id))
    statement = select([Task]).where(Task.task_id == task_id)
    task = submit_select(statement)
    if task:
        statement = delete(Task).where(Task.task_id == task_id)
        submit_sql(statement, priority=FOREGROUND)
        while get_task(task_id)[0]:
            sleep(0.01)
        return task[0], None
    else:
        return False, 'task:{} not found'.format(task_id)


@timed
def get_tasks():
    statement = select([Task])
    tasks = submit_select(statement)
    if tasks:
        return tasks, None
    return [], None


@timed
def get_task(task_id):
    statement = select([Task]).where(Task.task_id == task_id)
    task = submit_select(statement)
    if task:
        return task, None
    return False, 'task:{} not found'.format(task_id)


def db_filter(query: Query, field, operator, value):
    f = getattr(query.froms[0].columns, field)
    if operator == 'eq':
        return query.where(f == value)
    elif operator == 'neq':
        return query.where(f != value)
    elif operator == 'lt':
        return query.where(f < value)
    elif operator == 'leq':
        return query.where(f <= value)
    elif operator == 'gt':
        return query.where(f > value)
    elif operator == 'geq':
        return query.where(f >= value)
    elif operator == 'like':
        return query.where(f.like("%" + str(value) + "%"))
    else:
        raise NotImplementedError(
            "Operator '{}' is Not Implemented".format(operator))


def apply_db_filter(query: Query, request_values):
    for key, value in request_values.items():
        if key in ['page_size', 'page', 'sort']:
            continue
        if ":" in value:
            operator, v = value.split(":", 1)
        else:
            operator = 'eq'
            v = value
        query = db_filter(query, key, operator, v)
    return query


def apply_db_sort(query: Query, request_values):
    sort_by = request_values.get("sort", "")
    sort_fields = sort_by.split(",")
    list_fields = list()
    for field in sort_fields:
        f = getattr(query.froms[0].columns, field.lstrip('-'))
        if field.startswith('-'):
            list_fields.append(str(f.desc()))
        else:
            list_fields.append(str(f.asc()))
    order = text(",".join(list_fields))
    query = query.order_by(order)
    return query


@timed
def get_file_num(task_id, request_values):
    query = select([FileList.id]).where(FileList.task_id == task_id)
    query = apply_db_filter(query, request_values)
    total = len(submit_select(query))

    return total


@timed
def get_progress_num(task_id, request_values):
    query = select([CommandOutput.id]).where(CommandOutput.task_id == task_id)
    query = apply_db_filter(query, request_values)
    total = len(submit_select(query))
    return total


@timed
def get_files(task_id, start, stop, request_values):
    f = select([FileList]).where(FileList.task_id == task_id)
    f = apply_db_filter(f, request_values)
    if request_values.get("sort", None):
        f = apply_db_sort(f, request_values)
    f = f.offset(start).limit(stop - start)
    files = submit_select(f)

    for file in files:
        filename = file.filename
        size = file.size
        ctime = file.ctime
        mtime = file.mtime
        mode = file.mode
        uid = file.uid
        gid = file.gid
        row_id = file.id
        yield(filename, size, ctime, mtime, mode, uid, gid, row_id)


@timed
def get_progress(task_id, start, stop, request_values):
    f = select([CommandOutput]).where(CommandOutput.task_id == task_id)
    f = apply_db_filter(f, request_values)
    f = f.order_by(CommandOutput.id)
    f = f.offset(start).limit(stop - start)
    lines = submit_select(f)

    for line in lines:
        yield(line.id, line.line, line.timestamp, line.stdstream)


@timed
def delete_old_tasks():
    old_tasks = select([Task.task_id]).order_by(
        Task.task_id.desc()).offset(MAX_TASKS).limit(MAX_TASKS)
    statement = delete(Task).where(Task.task_id.in_(old_tasks))
    submit_sql(statement, priority=FOREGROUND)
    while submit_select(old_tasks):
        sleep(0.01)


@timed
def vacuum():
    statement = text("vacuum")
    submit_sql(statement)


@timed
def delete_running_tasks():
    session = Session()
    query: Query = session.query(Task.status).filter_by(status='RUNNING')
    deleted_rows = query.delete()
    log.info('Deleted {} running tasks'.format(deleted_rows))

