-- =====================================================
-- aiweb database initialization script (v1.0.10 FINAL)
-- =====================================================
-- PURPOSE:
--   Cold-start / new customer / disaster recovery init
--
-- GUARANTEES:
--   1. Schema matches CURRENT production database facts
--   2. All tables & sequences OWNED BY aiweb_user
--   3. aiweb_user has full runtime permissions
--   4. Compatible with FastAPI + SQLAlchemy runtime
--
-- WARNING:
--   This script ASSUMES EMPTY ENV and DROPS NOTHING
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
-- 3. Create tables (FACT-ALIGNED STRUCTURE)
--------------------------------------------------------

-- users (17 columns, aligned with production)
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
    last_login_at     TIMESTAMP WITHOUT TIME ZONE,

    account_status    VARCHAR
);

-- plans
CREATE TABLE plans (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL,
    description     VARCHAR,
    quota           INTEGER NOT NULL,
    duration_days   INTEGER,
    price           NUMERIC DEFAULT 0,
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
-- 4. Indexes (FACT-ALIGNED)
--------------------------------------------------------

-- users
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_phone ON users (phone);
CREATE UNIQUE INDEX users_invitation_code_key ON users (invitation_code);

CREATE INDEX ix_users_id ON users (id);
CREATE INDEX idx_users_account_status ON users (account_status);

-- histories
CREATE INDEX ix_histories_id ON histories (id);
CREATE INDEX ix_histories_task_id ON histories (task_id);

-- quota_logs
CREATE INDEX idx_quota_logs_user_id ON quota_logs (user_id);
CREATE INDEX idx_quota_logs_created_at ON quota_logs (created_at);


--------------------------------------------------------
-- 5. Fix ownership (CRITICAL)
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
-- 6. Initialize admin user (OPTIONAL, FACT-COMPATIBLE)
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
    account_status,
    created_at
) VALUES (
    'admin',
    '$argon2id$v=19$m=65536,t=3,p=4$REPLACE_WITH_REAL_HASH',
    'admin@example.com',
    'admin',
    99,
    true,
    false,
    'normal',
    now()
);


--------------------------------------------------------
-- 7. Final sanity check (manual)
--------------------------------------------------------
-- \dt
-- SELECT id, username, role, account_status FROM users;
-- \d users
--------------------------------------------------------

-- END OF FILE
