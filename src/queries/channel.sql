-- name: GetUserByID :one
SELECT "id", "username", "given_name", "family_name", "enabled"
FROM "public"."user"
WHERE "id"=$1
;

-- name: CreateUser :exec
INSERT INTO "public"."user"
("id", "username", "given_name", "family_name", "enabled")
VALUES($1, $2, $3, $4, $5)
;

-- name: ChanListByUserID :many
SELECT "channel"."id", "channel"."channel", "channel"."title", "channel"."default"
FROM "public"."channel"
JOIN "public"."user_channel" ON "user_channel"."chan_id" = "channel"."id"
WHERE "user_channel"."user_id"=$1
;

-- name: UserListByChanID :many
SELECT "user"."id", "user"."username", "user"."given_name", "user"."family_name", "user"."enabled"
FROM "public"."user"
JOIN "public"."user_channel" ON "user_channel"."user_id" = "user"."id"
WHERE "user_channel"."chan_id"=$1
;


-- name: UserCanPublish :one
SELECT EXISTS (
    SELECT 1
    FROM "user_channel"
    WHERE
        "user_id" = (SELECT "id" FROM "user" WHERE "user"."id" = $1) AND
        "chan_id" = (SELECT "id" FROM "channel" WHERE "channel" = $2) AND
        "can_publish" = true
) AS "can_publish";