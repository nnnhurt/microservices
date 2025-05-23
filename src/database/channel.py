# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.29.0
# source: channel.sql
import dataclasses
from typing import Iterator, Optional
import uuid

import sqlalchemy

from . import models


CHAN_LIST_BY_USER_ID = """-- name: chan_list_by_user_id \\:many
SELECT "channel"."id", "channel"."channel", "channel"."title", "channel"."default"
FROM "public"."channel"
JOIN "public"."user_channel" ON "user_channel"."chan_id" = "channel"."id"
WHERE "user_channel"."user_id"=:p1
"""


CREATE_USER = """-- name: create_user \\:exec
INSERT INTO "public"."user"
("id", "username", "given_name", "family_name", "enabled")
VALUES(:p1, :p2, :p3, :p4, :p5)
"""


@dataclasses.dataclass()
class CreateUserParams:
    id: uuid.UUID
    username: str
    given_name: str
    family_name: str
    enabled: bool


GET_USER_BY_ID = """-- name: get_user_by_id \\:one
SELECT "id", "username", "given_name", "family_name", "enabled"
FROM "public"."user"
WHERE "id"=:p1
"""


USER_CAN_PUBLISH = """-- name: user_can_publish \\:one
SELECT EXISTS (
    SELECT 1
    FROM "user_channel"
    WHERE
        "user_id" = (SELECT "id" FROM "user" WHERE "user"."id" = :p1) AND
        "chan_id" = (SELECT "id" FROM "channel" WHERE "channel" = :p2) AND
        "can_publish" = true
) AS "can_publish"
"""


USER_LIST_BY_CHAN_ID = """-- name: user_list_by_chan_id \\:many
SELECT "user"."id", "user"."username", "user"."given_name", "user"."family_name", "user"."enabled"
FROM "public"."user"
JOIN "public"."user_channel" ON "user_channel"."user_id" = "user"."id"
WHERE "user_channel"."chan_id"=:p1
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def chan_list_by_user_id(self, *, user_id: uuid.UUID) -> Iterator[models.Channel]:
        result = self._conn.execute(sqlalchemy.text(CHAN_LIST_BY_USER_ID), {"p1": user_id})
        for row in result:
            yield models.Channel(
                id=row[0],
                channel=row[1],
                title=row[2],
                default=row[3],
            )

    def create_user(self, arg: CreateUserParams) -> None:
        self._conn.execute(sqlalchemy.text(CREATE_USER), {
            "p1": arg.id,
            "p2": arg.username,
            "p3": arg.given_name,
            "p4": arg.family_name,
            "p5": arg.enabled,
        })

    def get_user_by_id(self, *, id: uuid.UUID) -> Optional[models.User]:
        row = self._conn.execute(sqlalchemy.text(GET_USER_BY_ID), {"p1": id}).first()
        if row is None:
            return None
        return models.User(
            id=row[0],
            username=row[1],
            given_name=row[2],
            family_name=row[3],
            enabled=row[4],
        )

    def user_can_publish(self, *, id: uuid.UUID, channel: str) -> Optional[bool]:
        row = self._conn.execute(sqlalchemy.text(USER_CAN_PUBLISH), {"p1": id, "p2": channel}).first()
        if row is None:
            return None
        return row[0]

    def user_list_by_chan_id(self, *, chan_id: int) -> Iterator[models.User]:
        result = self._conn.execute(sqlalchemy.text(USER_LIST_BY_CHAN_ID), {"p1": chan_id})
        for row in result:
            yield models.User(
                id=row[0],
                username=row[1],
                given_name=row[2],
                family_name=row[3],
                enabled=row[4],
            )
