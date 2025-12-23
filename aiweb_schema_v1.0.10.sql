--
-- PostgreSQL database dump
--

\restrict uogi7AqLhFxIOOFWODtqJ99r8Kr14aVysH2Lby8u1aRswdkdjXuT9NyzTt84fBY

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

DROP INDEX IF EXISTS public.users_invitation_code_key;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_phone;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_histories_task_id;
DROP INDEX IF EXISTS public.ix_histories_id;
DROP INDEX IF EXISTS public.idx_users_account_status;
DROP INDEX IF EXISTS public.idx_quota_logs_user_id;
DROP INDEX IF EXISTS public.idx_quota_logs_created_at;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.quota_logs DROP CONSTRAINT IF EXISTS quota_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.plans DROP CONSTRAINT IF EXISTS plans_pkey;
ALTER TABLE IF EXISTS ONLY public.histories DROP CONSTRAINT IF EXISTS histories_pkey;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.quota_logs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.plans ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.histories ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.quota_logs_id_seq;
DROP TABLE IF EXISTS public.quota_logs;
DROP SEQUENCE IF EXISTS public.plans_id_seq;
DROP TABLE IF EXISTS public.plans;
DROP SEQUENCE IF EXISTS public.histories_id_seq;
DROP TABLE IF EXISTS public.histories;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: histories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.histories (
    id integer NOT NULL,
    user_id integer,
    task_id character varying,
    prompt character varying NOT NULL,
    image_url character varying,
    created_at timestamp without time zone,
    status character varying DEFAULT 'pending'::character varying
);


--
-- Name: histories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.histories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: histories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.histories_id_seq OWNED BY public.histories.id;


--
-- Name: plans; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: plans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;


--
-- Name: quota_logs; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: quota_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quota_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quota_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quota_logs_id_seq OWNED BY public.quota_logs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
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
    account_status character varying(16) DEFAULT 'normal'::character varying NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: histories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.histories ALTER COLUMN id SET DEFAULT nextval('public.histories_id_seq'::regclass);


--
-- Name: plans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plans ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


--
-- Name: quota_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quota_logs ALTER COLUMN id SET DEFAULT nextval('public.quota_logs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: histories histories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.histories
    ADD CONSTRAINT histories_pkey PRIMARY KEY (id);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: quota_logs quota_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quota_logs
    ADD CONSTRAINT quota_logs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_quota_logs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_quota_logs_created_at ON public.quota_logs USING btree (created_at);


--
-- Name: idx_quota_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_quota_logs_user_id ON public.quota_logs USING btree (user_id);


--
-- Name: idx_users_account_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_account_status ON public.users USING btree (account_status);


--
-- Name: ix_histories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_histories_id ON public.histories USING btree (id);


--
-- Name: ix_histories_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_histories_task_id ON public.histories USING btree (task_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: users_invitation_code_key; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX users_invitation_code_key ON public.users USING btree (invitation_code);


--
-- PostgreSQL database dump complete
--

\unrestrict uogi7AqLhFxIOOFWODtqJ99r8Kr14aVysH2Lby8u1aRswdkdjXuT9NyzTt84fBY

