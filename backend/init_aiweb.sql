-- =====================================================
-- aiweb database initialization script (FINAL)
-- =====================================================
-- PURPOSE:
--   Cold-start / disaster recovery initialization
--
-- GUARANTEES:
--   1. All tables & sequences OWNED BY aiweb_user
--   2. aiweb_user has full runtime permissions
--   3. Compatible with FastAPI + SQLAlchemy runtime
--
-- WARNING:
--   This script DROPS NOTHING and ASSUMES EMPTY ENV.
-- =====================================================


--------------------------------------------------------
-- 1. Create database & user (run as postgres)
--------------------------------------------------------

CREATE DATABASE aiweb;

CREATE USER aiweb_user WITH PASSWORD 'REDACTED_PASSWORD';

GRANT ALL PRIVILEGES ON DATABASE aiweb TO aiweb_user;
ALTER DATABASE aiweb OWNER TO aiweb_user;


--------------------------------------------------------
-- 2. Connect & prepare schema
--------------------------------------------------------

\connect aiweb;

GRANT ALL ON SCHEMA public TO aiweb_user;
ALTER SCHEMA public OWNER TO aiweb_user;


--------------------------------------------------------
-- 3. Create tables (objects MAY be owned by postgres)
--    Ownership will be FIXED explicitly later
--------------------------------------------------------

-- users
CREATE TABLE users (
    id                SERIAL PRIMARY KEY,
    username          VARCHAR NOT NULL,
    password_hash     VARCHAR NOT NULL,
    email             VARCHAR,
    phone             VARCHAR,
    role              VARCHAR,
    quota             BIGINT,
    is_active         BOOLEAN,
    is_deleted        BOOLEAN,
    avatar_url        VARCHAR,
    remark            VARCHAR,
    inviter_id        INTEGER,
    invitation_code   VARCHAR,
    created_at        TIMESTAMP WITHOUT TIME ZONE,
    updated_at        TIMESTAMP WITHOUT TIME ZONE,
    last_login_at     TIMESTAMP WITHOUT TIME ZONE
);

-- plans
CREATE TABLE plans (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL,
    description     VARCHAR,
    quota           INTEGER NOT NULL,
    duration_days   INTEGER,
    price           INTEGER DEFAULT 0,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- histories
-- NOTE:
-- task_id ALLOWS NULL to support async generate workflow
CREATE TABLE histories (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER,
    task_id    VARCHAR,
    prompt     VARCHAR NOT NULL,
    image_url  VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    status     VARCHAR DEFAULT 'pending'
);

-- quota_logs
CREATE TABLE quota_logs (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER NOT NULL,
    change           INTEGER NOT NULL,
    reason           VARCHAR NOT NULL,
    operator_id      INTEGER,
    related_plan_id  INTEGER,
    created_at       TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


--------------------------------------------------------
-- 4. Indexes (aligned with legacy v1.0.0-beta)
--------------------------------------------------------

-- users
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_phone ON users (phone);
CREATE UNIQUE INDEX users_invitation_code_key ON users (invitation_code);
CREATE INDEX ix_users_id ON users (id);

-- histories
CREATE INDEX ix_histories_id ON histories (id);
CREATE INDEX ix_histories_task_id ON histories (task_id);

-- quota_logs
CREATE INDEX idx_quota_logs_user_id ON quota_logs (user_id);
CREATE INDEX idx_quota_logs_created_at ON quota_logs (created_at);


--------------------------------------------------------
-- 5. CRITICAL: Fix ownership (THIS IS THE KEY FIX)
--------------------------------------------------------

ALTER TABLE users OWNER TO aiweb_user;
ALTER TABLE plans OWNER TO aiweb_user;
ALTER TABLE histories OWNER TO aiweb_user;
ALTER TABLE quota_logs OWNER TO aiweb_user;

ALTER SEQUENCE users_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE plans_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE histories_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE quota_logs_id_seq OWNER TO aiweb_user;


--------------------------------------------------------
-- 6. Initialize admin user
--------------------------------------------------------
-- IMPORTANT:
-- Replace password_hash with a REAL argon2 hash
-- generated in the SAME venv as backend runtime.

INSERT INTO users (
    username,
    password_hash,
    email,
    role,
    quota,
    is_active,
    is_deleted,
    created_at
) VALUES (
    'admin',
    '$argon2id$v=19$m=65536,t=3,p=4$da4VwlirVUpJybmXcs4Z4w$gzhTghlaZ7BiJ6J+o4hZ0UpH8VDIyCtnE6ZYUny/n1Q',
    'admin@example.com',
    'admin',
    99,
    true,
    false,
    now()
);


--------------------------------------------------------
-- 7. Final sanity check (manual)
--------------------------------------------------------
-- \dt
-- SELECT id, username, role FROM users;
-- \d histories
--------------------------------------------------------

-- END OF FILE
