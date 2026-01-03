--
-- PostgreSQL database dump
--

\restrict dJEa27ARIAOUflof87PCsfniaaNA9CUHQLbH2Tz15eQqOqlCoHRNYDhHRMTGtFB

-- Dumped from database version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.20 (Ubuntu 14.20-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: histories; Type: TABLE; Schema: public; Owner: aiweb_user
--

CREATE TABLE public.histories (
    id integer NOT NULL,
    user_id integer,
    task_id character varying,
    prompt character varying NOT NULL,
    image_url character varying,
    created_at timestamp without time zone,
    status character varying DEFAULT 'pending'::character varying,
    honor_consumed_at timestamp without time zone,
    user_fact_consumed_at timestamp without time zone,
    archive_url character varying,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    total_elapsed_time integer
);


ALTER TABLE public.histories OWNER TO aiweb_user;

--
-- Name: COLUMN histories.started_at; Type: COMMENT; Schema: public; Owner: aiweb_user
--

COMMENT ON COLUMN public.histories.started_at IS '任务实际开始执行时间（UTC），仅用于内部执行统计';


--
-- Name: COLUMN histories.completed_at; Type: COMMENT; Schema: public; Owner: aiweb_user
--

COMMENT ON COLUMN public.histories.completed_at IS '任务最终完成时间（UTC），定义为 archive_url 写入完成时间';


--
-- Name: COLUMN histories.total_elapsed_time; Type: COMMENT; Schema: public; Owner: aiweb_user
--

COMMENT ON COLUMN public.histories.total_elapsed_time IS '任务真实完成耗时（秒），定义为 completed_at - created_at，仅用于历史页面展示';


--
-- Name: histories_id_seq; Type: SEQUENCE; Schema: public; Owner: aiweb_user
--

CREATE SEQUENCE public.histories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.histories_id_seq OWNER TO aiweb_user;

--
-- Name: histories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aiweb_user
--

ALTER SEQUENCE public.histories_id_seq OWNED BY public.histories.id;


--
-- Name: honor_level_events; Type: TABLE; Schema: public; Owner: aiweb_user
--

CREATE TABLE public.honor_level_events (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    trigger character varying(50) NOT NULL,
    before_total_success_tasks integer NOT NULL,
    after_total_success_tasks integer NOT NULL,
    before_star integer NOT NULL,
    after_star integer NOT NULL,
    before_moon integer NOT NULL,
    after_moon integer NOT NULL,
    before_sun integer NOT NULL,
    after_sun integer NOT NULL,
    before_diamond integer NOT NULL,
    after_diamond integer NOT NULL,
    before_crown integer NOT NULL,
    after_crown integer NOT NULL,
    reward_quota_delta integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.honor_level_events OWNER TO aiweb_user;

--
-- Name: honor_level_events_id_seq; Type: SEQUENCE; Schema: public; Owner: aiweb_user
--

CREATE SEQUENCE public.honor_level_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.honor_level_events_id_seq OWNER TO aiweb_user;

--
-- Name: honor_level_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aiweb_user
--

ALTER SEQUENCE public.honor_level_events_id_seq OWNED BY public.honor_level_events.id;


--
-- Name: plans; Type: TABLE; Schema: public; Owner: aiweb_user
--

CREATE TABLE public.plans (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    quota integer NOT NULL,
    duration_days integer,
    price numeric(10,2) DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.plans OWNER TO aiweb_user;

--
-- Name: plans_id_seq; Type: SEQUENCE; Schema: public; Owner: aiweb_user
--

CREATE SEQUENCE public.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.plans_id_seq OWNER TO aiweb_user;

--
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aiweb_user
--

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;


--
-- Name: quota_logs; Type: TABLE; Schema: public; Owner: aiweb_user
--

CREATE TABLE public.quota_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    change integer NOT NULL,
    reason character varying NOT NULL,
    operator_id integer,
    related_plan_id integer,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.quota_logs OWNER TO aiweb_user;

--
-- Name: quota_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: aiweb_user
--

CREATE SEQUENCE public.quota_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quota_logs_id_seq OWNER TO aiweb_user;

--
-- Name: quota_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aiweb_user
--

ALTER SEQUENCE public.quota_logs_id_seq OWNED BY public.quota_logs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: aiweb_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    password_hash character varying NOT NULL,
    email character varying,
    phone character varying,
    role character varying,
    quota bigint,
    is_active boolean,
    is_deleted boolean,
    avatar_url character varying,
    remark character varying,
    inviter_id integer,
    invitation_code character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login_at timestamp without time zone,
    account_status character varying(16) DEFAULT 'normal'::character varying NOT NULL,
    total_success_tasks integer DEFAULT 0 NOT NULL,
    level_star integer DEFAULT 0 NOT NULL,
    level_moon integer DEFAULT 0 NOT NULL,
    level_sun integer DEFAULT 0 NOT NULL,
    level_diamond integer DEFAULT 0 NOT NULL,
    level_crown integer DEFAULT 0 NOT NULL,
    user_fact_consumed_at timestamp without time zone
);


ALTER TABLE public.users OWNER TO aiweb_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: aiweb_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO aiweb_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aiweb_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: histories id; Type: DEFAULT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.histories ALTER COLUMN id SET DEFAULT nextval('public.histories_id_seq'::regclass);


--
-- Name: honor_level_events id; Type: DEFAULT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.honor_level_events ALTER COLUMN id SET DEFAULT nextval('public.honor_level_events_id_seq'::regclass);


--
-- Name: plans id; Type: DEFAULT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.plans ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


--
-- Name: quota_logs id; Type: DEFAULT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.quota_logs ALTER COLUMN id SET DEFAULT nextval('public.quota_logs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: histories histories_pkey; Type: CONSTRAINT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.histories
    ADD CONSTRAINT histories_pkey PRIMARY KEY (id);


--
-- Name: honor_level_events honor_level_events_pkey; Type: CONSTRAINT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.honor_level_events
    ADD CONSTRAINT honor_level_events_pkey PRIMARY KEY (id);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: quota_logs quota_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.quota_logs
    ADD CONSTRAINT quota_logs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: aiweb_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_histories_honor_consumed_at; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX idx_histories_honor_consumed_at ON public.histories USING btree (honor_consumed_at);


--
-- Name: idx_quota_logs_created_at; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX idx_quota_logs_created_at ON public.quota_logs USING btree (created_at);


--
-- Name: idx_quota_logs_user_id; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX idx_quota_logs_user_id ON public.quota_logs USING btree (user_id);


--
-- Name: idx_users_account_status; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX idx_users_account_status ON public.users USING btree (account_status);


--
-- Name: ix_histories_id; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX ix_histories_id ON public.histories USING btree (id);


--
-- Name: ix_histories_task_id; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX ix_histories_task_id ON public.histories USING btree (task_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE UNIQUE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: users_invitation_code_key; Type: INDEX; Schema: public; Owner: aiweb_user
--

CREATE UNIQUE INDEX users_invitation_code_key ON public.users USING btree (invitation_code);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: aiweb_user
--

REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO aiweb_user;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict dJEa27ARIAOUflof87PCsfniaaNA9CUHQLbH2Tz15eQqOqlCoHRNYDhHRMTGtFB

