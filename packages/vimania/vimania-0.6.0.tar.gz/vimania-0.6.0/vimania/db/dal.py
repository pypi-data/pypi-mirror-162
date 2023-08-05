import logging
from datetime import datetime
from enum import IntEnum
from typing import Sequence, Optional

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.engine import Engine, Connection

# from twbm.environment import Environment

_log = logging.getLogger("vimania-plugin.dal")
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

metadata = sa.MetaData()

sim_results_table = sa.Table(
    "vimania_todos",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("parent_id", sa.Integer, ForeignKey("vimania_todos.id"), nullable=True),
    sa.Column("todo", sa.String(), nullable=False, unique=True),
    sa.Column("metadata", sa.String(), default=""),
    sa.Column("tags", sa.String(), default=""),
    sa.Column("desc", sa.String(), default=""),
    sa.Column("path", sa.String(), default=""),
    sa.Column("flags", sa.Integer(), default=0),
    sa.Column(
        "last_update_ts", sa.DateTime(), server_default=sa.func.current_timestamp()
    ),
    sa.Column("created_at", sa.DateTime()),
)


# if not flags are set: value=0, allows boolean operations
class TodoStatus(IntEnum):
    OPEN = 1
    PROGRESS = 2
    DONE = 4
    TODELETE = 8


class Todo(BaseModel):
    id: int = None
    parent_id: int = None
    todo: str = ""
    metadata: str = ""
    tags: str = ",,"
    desc: str = ""
    path: str = ""  # file location
    flags: int = 0  # TodoStatus
    last_update_ts: datetime = datetime.utcnow()
    created_at: datetime = None

    @property
    def split_tags(self) -> Sequence[str]:
        return [tag for tag in self.tags.split(",") if tag != ""]


# noinspection PyPropertyAccess
class DAL:
    _sql_alchemy_db_engine: Engine
    _conn: Connection

    is_simulated_environment: bool

    def __init__(self, env_config: "Environment"):
        self.bm_db_url = env_config.tw_vimania_db_url
        _log.debug(f"Using database: {self.bm_db_url}")

    def __enter__(self):
        self._sql_alchemy_db_engine: Engine = create_engine(self.bm_db_url)
        self._conn = self._sql_alchemy_db_engine.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._conn.close()
        self._sql_alchemy_db_engine.dispose()

    @property
    def conn(self):
        return self._conn

    def get_overall_status(self, id_: int) -> Optional[int]:
        """returns the minimal flag of all children,
        None if no children, or not found
        """
        query = """
            with recursive tds_children as (
                select id,
                       parent_id,
                       todo,
                       metadata,
                       tags,
                       desc,
                       path,
                       flags,
                       last_update_ts,
                       created_at,
                       0 as depth
                from vimania_todos
                where id == :id_
                  and flags <= 4
                union all
                select vimania_todos.id,
                       vimania_todos.parent_id,
                       vimania_todos.todo,
                       vimania_todos.metadata,
                       vimania_todos.tags,
                       vimania_todos.desc,
                       vimania_todos.path,
                       vimania_todos.flags,
                       vimania_todos.last_update_ts,
                       vimania_todos.created_at,
                       tds_children.depth + 1
                from vimania_todos
                         join tds_children
                where vimania_todos.parent_id == tds_children.id
                  and vimania_todos.flags <= 4
            )
            select min(flags) overall_status
            from tds_children
            where id != :id_
            --where level < 3  -- only one level down
            ;
        """
        result = self.conn.execute(query, id_=id_).all()
        _log.debug(f"{id_=}, {result=}")
        self.conn.connection.commit()
        try:
            return result[0][0]
        except IndexError:
            _log.error(f"Index Error.")
            return None

    def get_depth(self, id_: int) -> int:
        query = """
            with recursive tds_parents as (
                select id, parent_id, todo, 0 as depth
                from vimania_todos
                where id == :id_
                  and flags <= 4
                union all
                select vimania_todos.id, vimania_todos.parent_id, vimania_todos.todo, tds_parents.depth - 1
                from vimania_todos
                         join tds_parents
                where vimania_todos.id == tds_parents.parent_id
                  and vimania_todos.flags < 4
            )
            select depth
            from tds_parents
            order by depth
            limit 1
            ;
        """
        result = self.conn.execute(query, id_=id_).all()
        _log.debug(f"{id_=}, {result=}")
        self.conn.connection.commit()
        try:
            return result[0][0]
        except IndexError:
            return 0

    def get_todo_parent(self, id_: int, depth: int) -> Todo:
        query = """
            with recursive tds_parents as (
                select id,
                       parent_id,
                       todo,
                       metadata,
                       tags,
                       desc,
                       path,
                       flags,
                       last_update_ts,
                       created_at,
                       0 as depth
                from vimania_todos
                where id = :id_
                  and flags <= 4
                union all
                select vimania_todos.id,
                       vimania_todos.parent_id,
                       vimania_todos.todo,
                       vimania_todos.metadata,
                       vimania_todos.tags,
                       vimania_todos.desc,
                       vimania_todos.path,
                       vimania_todos.flags,
                       vimania_todos.last_update_ts,
                       vimania_todos.created_at,
                       tds_parents.depth - 1
                from vimania_todos
                         join tds_parents
                where vimania_todos.id == tds_parents.parent_id
                  and vimania_todos.flags <= 4
            )
            select *
            from tds_parents
            where depth = :depth
            ;
        """
        result = self.conn.execute(query, id_=id_, depth=depth).all()
        assert len(result) == 1, f"Ambigouus parents: {result=}, {id_=}"
        self.conn.connection.commit()
        return result[0]

    def delete_todo(self, id: int) -> int:
        query = """
            delete from vimania_todos where id = :id_
            -- returning *  -- not working!
            ;
        """
        result = self.conn.execute(
            query, id_=id
        )  # TODO: check result and returning clause
        self.conn.connection.commit()
        return result

    def insert_todo(self, todo: Todo) -> int:
        query = """
            -- name: insert_todo<!
            -- record_class: Todo
            insert into vimania_todos (parent_id, todo, metadata, tags, desc, path, flags, created_at)
            values (:parent_id, :todo, :metadata, :tags, :desc, :path, :flags, :created_at)
            returning *;
        """
        result = self.conn.execute(
            query,
            parent_id=todo.parent_id,
            todo=todo.todo,
            metadata=todo.metadata,
            tags=todo.tags,
            desc=todo.desc,
            path=todo.path,
            flags=todo.flags,
            created_at=datetime.utcnow(),
        ).all()
        self.conn.connection.commit()
        return result[0][0]

    def update_todo(self, todo: Todo) -> int:
        query = """
            -- name: update_todo<!
            update vimania_todos
            set parent_id = :parent_id, todo = :todo, metadata = :metadata, tags = :tags, flags = :flags, desc = :desc, path = :path 
            where id = :id
            returning *;
        """
        result = self.conn.execute(
            query,
            id=todo.id,
            parent_id=todo.parent_id,
            todo=todo.todo,
            metadata=todo.metadata,
            tags=todo.tags,
            flags=todo.flags,
            desc=todo.desc,
            path=todo.path,
        ).all()
        self.conn.connection.commit()
        # return result  # shows the last used id
        # TODO: handling non existing todo
        return result[0][0]

    def get_todo_by_id(self, id_: int) -> Todo:
        # Example query
        # noinspection SqlResolve
        query = """
            -- name: get_todo_by_id^
            -- record_class: Todo
            select *
            from vimania_todos
            where id = :id;
            """
        sql_result = self.conn.execute(query, id=id_).all()
        if not sql_result:
            # noinspection PyRedundantParentheses
            return Todo()
        return Todo(**(sql_result[0]))

    def get_todos(self, fts_query: str) -> Sequence[Todo]:
        # Example query
        # noinspection SqlResolve
        if fts_query != "":
            query = """
                -- name: get_todos
                -- record_class: Todo
                select *
                from vimania_todos_fts
                where vimania_todos_fts match :fts_query
                order by rank;
            """
            sql_result = self.conn.execute(query, fts_query=fts_query).all()
        else:  # TODO: make normal query
            query = """
                -- name: get_todos
                -- record_class: Todo
                select *
                from vimania_todos_fts
                order by rank;
            """
            sql_result = self.conn.execute(query, fts_query=fts_query).all()

        if not sql_result:
            # noinspection PyRedundantParentheses
            return (Todo(),)
        return [Todo(**todo) for todo in sql_result]

    def get_related_tags(self, tag: str):
        tag_query = f"%,{tag},%"
        # noinspection SqlResolve
        query = """
            -- name: get_related_tags
            with RECURSIVE split(tags, rest) AS (
                SELECT '', tags || ','
                FROM vimania_todos
                WHERE tags LIKE :tag_query
                -- WHERE tags LIKE '%,ccc,%'
                UNION ALL
                SELECT substr(rest, 0, instr(rest, ',')),
                       substr(rest, instr(rest, ',') + 1)
                FROM split
                WHERE rest <> '')
            SELECT distinct tags
            FROM split
            WHERE tags <> ''
            ORDER BY tags;
        """
        sql_result = self.conn.execute(
            query,
            tag_query=tag_query,
        ).all()
        return [tags[0] for tags in sql_result]

    def get_all_tags(self):
        # noinspection SqlResolve
        query = """
            -- name: get_all_tags
            with RECURSIVE split(tags, rest) AS (
                SELECT '', tags || ','
                FROM vimania_todos
                UNION ALL
                SELECT substr(rest, 0, instr(rest, ',')),
                       substr(rest, instr(rest, ',') + 1)
                FROM split
                WHERE rest <> '')
            SELECT distinct tags
            FROM split
            WHERE tags <> ''
            ORDER BY tags;
        """
        sql_result = self.conn.execute(
            query,
        ).all()

        return [tags[0] for tags in sql_result]
