-- =====================================================
-- aiweb database initialization script (v1.0.30 FINAL)
-- =====================================================
-- PURPOSE:
--   Cold-start / new customer / disaster recovery init
--
-- GUARANTEES:
--   1. Schema matches v1.0.30 PRODUCTION DATABASE FACTS
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
-- 3. Create tables (v1.0.30 FACT-ALIGNED)
--------------------------------------------------------

-- users
CREATE TABLE public.users (
    id                  INTEGER NOT NULL,
    username            CHARACTER VARYING NOT NULL,
    password_hash       CHARACTER VARYING NOT NULL,
    email               CHARACTER VARYING,
    phone               CHARACTER VARYING,
    role                CHARACTER VARYING,

    quota               BIGINT,
    is_active           BOOLEAN,
    is_deleted          BOOLEAN,

    avatar_url          CHARACTER VARYING,
    remark              CHARACTER VARYING,
    inviter_id          INTEGER,
    invitation_code     CHARACTER VARYING,

    created_at          TIMESTAMP WITHOUT TIME ZONE,
    updated_at          TIMESTAMP WITHOUT TIME ZONE,
    last_login_at       TIMESTAMP WITHOUT TIME ZONE,

    account_status      CHARACTER VARYING(16) DEFAULT 'normal' NOT NULL,

    total_success_tasks INTEGER DEFAULT 0 NOT NULL,
    level_star          INTEGER DEFAULT 0 NOT NULL,
    level_moon          INTEGER DEFAULT 0 NOT NULL,
    level_sun           INTEGER DEFAULT 0 NOT NULL,
    level_diamond       INTEGER DEFAULT 0 NOT NULL,
    level_crown         INTEGER DEFAULT 0 NOT NULL,

    user_fact_consumed_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE SEQUENCE public.users_id_seq
    AS INTEGER
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE ONLY public.users
    ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


-- plans
CREATE TABLE public.plans (
    id              INTEGER NOT NULL,
    name            CHARACTER VARYING NOT NULL,
    description     CHARACTER VARYING,
    quota           INTEGER NOT NULL,
    duration_days   INTEGER,
    price           NUMERIC(10,2) DEFAULT 0,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE SEQUENCE public.plans_id_seq
    AS INTEGER
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;
ALTER TABLE ONLY public.plans
    ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


-- histories
CREATE TABLE public.histories (
    id                  INTEGER NOT NULL,
    user_id             INTEGER,
    task_id             CHARACTER VARYING,
    prompt              CHARACTER VARYING NOT NULL,
    image_url           CHARACTER VARYING,
    archive_url         CHARACTER VARYING,
    created_at          TIMESTAMP WITHOUT TIME ZONE,
    status              CHARACTER VARYING DEFAULT 'pending',
    honor_consumed_at   TIMESTAMP WITHOUT TIME ZONE,
    user_fact_consumed_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE SEQUENCE public.histories_id_seq
    AS INTEGER
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.histories_id_seq OWNED BY public.histories.id;
ALTER TABLE ONLY public.histories
    ALTER COLUMN id SET DEFAULT nextval('public.histories_id_seq'::regclass);


-- honor_level_events
CREATE TABLE public.honor_level_events (
    id                          BIGINT NOT NULL,
    user_id                     INTEGER NOT NULL,
    trigger                     CHARACTER VARYING(50) NOT NULL,

    before_total_success_tasks  INTEGER NOT NULL,
    after_total_success_tasks   INTEGER NOT NULL,

    before_star                 INTEGER NOT NULL,
    after_star                  INTEGER NOT NULL,
    before_moon                 INTEGER NOT NULL,
    after_moon                  INTEGER NOT NULL,
    before_sun                  INTEGER NOT NULL,
    after_sun                   INTEGER NOT NULL,
    before_diamond              INTEGER NOT NULL,
    after_diamond               INTEGER NOT NULL,
    before_crown                INTEGER NOT NULL,
    after_crown                 INTEGER NOT NULL,

    reward_quota_delta          INTEGER DEFAULT 0 NOT NULL,
    created_at                  TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE SEQUENCE public.honor_level_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.honor_level_events_id_seq OWNED BY public.honor_level_events.id;
ALTER TABLE ONLY public.honor_level_events
    ALTER COLUMN id SET DEFAULT nextval('public.honor_level_events_id_seq'::regclass);


-- quota_logs
CREATE TABLE public.quota_logs (
    id               INTEGER NOT NULL,
    user_id          INTEGER NOT NULL,
    change           INTEGER NOT NULL,
    reason           CHARACTER VARYING NOT NULL,
    operator_id      INTEGER,
    related_plan_id  INTEGER,
    created_at       TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE SEQUENCE public.quota_logs_id_seq
    AS INTEGER
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.quota_logs_id_seq OWNED BY public.quota_logs.id;
ALTER TABLE ONLY public.quota_logs
    ALTER COLUMN id SET DEFAULT nextval('public.quota_logs_id_seq'::regclass);


--------------------------------------------------------
-- 4. Constraints
--------------------------------------------------------

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.histories
    ADD CONSTRAINT histories_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.quota_logs
    ADD CONSTRAINT quota_logs_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.honor_level_events
    ADD CONSTRAINT honor_level_events_pkey PRIMARY KEY (id);


--------------------------------------------------------
-- 5. Indexes (v1.0.30 FACT)
--------------------------------------------------------

-- users
CREATE UNIQUE INDEX ix_users_username ON public.users (username);
CREATE UNIQUE INDEX ix_users_email ON public.users (email);
CREATE UNIQUE INDEX ix_users_phone ON public.users (phone);
CREATE UNIQUE INDEX users_invitation_code_key ON public.users (invitation_code);
CREATE INDEX ix_users_id ON public.users (id);
CREATE INDEX idx_users_account_status ON public.users (account_status);

-- histories
CREATE INDEX ix_histories_id ON public.histories (id);
CREATE INDEX ix_histories_task_id ON public.histories (task_id);
CREATE INDEX idx_histories_honor_consumed_at ON public.histories (honor_consumed_at);

-- quota_logs
CREATE INDEX idx_quota_logs_user_id ON public.quota_logs (user_id);
CREATE INDEX idx_quota_logs_created_at ON public.quota_logs (created_at);


--------------------------------------------------------
-- 6. Ownership (CRITICAL)
--------------------------------------------------------

ALTER TABLE users OWNER TO aiweb_user;
ALTER TABLE plans OWNER TO aiweb_user;
ALTER TABLE histories OWNER TO aiweb_user;
ALTER TABLE quota_logs OWNER TO aiweb_user;
ALTER TABLE honor_level_events OWNER TO aiweb_user;

ALTER SEQUENCE users_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE plans_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE histories_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE quota_logs_id_seq OWNER TO aiweb_user;
ALTER SEQUENCE honor_level_events_id_seq OWNER TO aiweb_user;


--------------------------------------------------------
-- 7. Initialize admin user (OPTIONAL, FACT-COMPATIBLE)
--------------------------------------------------------
-- IMPORTANT:
-- password_hash MUST be generated with the same argon2 params
-- as backend runtime.

INSERT INTO public.users (
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
-- 8. Final sanity check (manual)
--------------------------------------------------------
-- \dt
-- \d users
-- SELECT id, username, total_success_tasks FROM users;
--------------------------------------------------------

-- END OF FILE
