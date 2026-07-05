--
-- PostgreSQL database dump
--

\restrict xzcLDgfJRE9ZXvI0dENXRyvNh2sYOmJ68Puwo2We4VadlALaJeAFctptDaBliEH

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, created_at) FROM stdin;
1	david	scrypt:32768:8:1$ezN03iDLcLogtAaw$e8c860651f3ab3aed44a6ed18dcba8763eeb09019860f4fc6655f9ed6aa623732b203270145cbabf044b072f54c94ee05c3b895b942907ac3a89cacab8beac98	2025-11-27 17:51:09.371252
2	david12345	scrypt:32768:8:1$bbpfIrQitlePFEIm$64a8db5f2fdc09778bd0e13466180c15c7c9fedcee2c02a90d45018e41eb0b14667e25e2745c143dfe11e008f932d534cfd9ba91b6826f64b0edb3bd7d41271e	2025-11-27 18:04:58.808672
3	davidmg	scrypt:32768:8:1$cZ5oiL9w2Wcqy9KP$87bb92c1bdf908b522facafd9be3c3fbc4798fabf34c2c5bb5b815d76750de159205dba704a380a0f1c6730795d43831cbeda22d3647136fa1911e74e3f4e23d	2025-11-27 18:26:22.512079
4	123145	scrypt:32768:8:1$x3pnWRXFhWtUiil1$4db22e76bd0d32048c67171faff5185c959772f45adc189952ffd93c1aedd2283b59a50a20ba805dfedd9d55fb8682f7550d029334c32090819fe106dec2cca4	2025-11-27 18:49:48.600713
5	testuser	scrypt:32768:8:1$QYZ3FzbboVYxFX4l$b71f3df439e4cf9fbdf93085a7f046ee51b620714209113e44088122aabfe4c3af8607c84b9f3d8679925f4a0349e7486198a8a22e1d2160de28e1823b4571eb	2025-11-27 19:00:19.975526
6	davidmg5	scrypt:32768:8:1$BqTJ0kbSEdmKahCG$bb609d02d12badcb9353fb08fd5a9802cf129edb7ee93e8aaea87a5343833c3dcb13a3106d87bb30f87a65bfaeb95eefe8a10fd1a5149b9f72c1928133ef7cf8	2025-11-27 19:01:28.775824
7	david75	scrypt:32768:8:1$GQAJXY3HCj9bxbjM$bc7352d3300e9ef45e5aa394cc90748795308769cff9f31c1cbd215566c053bd66b4fe8d64521a3b36d42b2900f1e268af80afd221e938882ea8c8af741a1d77	2025-11-27 19:04:00.760769
8	davidmarkowski	scrypt:32768:8:1$OlftXRipFtyVeYav$fa4724a970c95a13478da686bed9da73ee4282694c0f698689fc3c9e554918c2b29190513c108422d73207228bc1a43f8d6f5b9a8b3d967157acd084ff2eebcf	2025-11-27 21:35:08.173738
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 8, true);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: -
--

GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;


--
-- PostgreSQL database dump complete
--

\unrestrict xzcLDgfJRE9ZXvI0dENXRyvNh2sYOmJ68Puwo2We4VadlALaJeAFctptDaBliEH

