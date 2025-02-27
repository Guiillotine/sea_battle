PGDMP      (                 }         
   sea_battle    12.22    16.0 -    0           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            1           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            2           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            3           1262    16530 
   sea_battle    DATABASE     ~   CREATE DATABASE sea_battle WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE sea_battle;
                postgres    false                        2615    2200    public    SCHEMA     2   -- *not* creating schema, since initdb creates it
 2   -- *not* dropping schema, since initdb creates it
                postgres    false            4           0    0    SCHEMA public    ACL     Q   REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;
                   postgres    false    7            �            1259    25007    game    TABLE       CREATE TABLE public.game (
    id integer NOT NULL,
    sid character varying,
    board json,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    id_player1 integer,
    id_player2 integer,
    id_winner integer,
    id_status integer
);
    DROP TABLE public.game;
       public         heap    postgres    false    7            �            1259    25013    game_id_seq    SEQUENCE     �   CREATE SEQUENCE public.game_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.game_id_seq;
       public          postgres    false    202    7            5           0    0    game_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.game_id_seq OWNED BY public.game.id;
          public          postgres    false    203            �            1259    25015    player    TABLE     �   CREATE TABLE public.player (
    id integer NOT NULL,
    sid character varying,
    login character varying,
    password character varying
);
    DROP TABLE public.player;
       public         heap    postgres    false    7            �            1259    25021    player_id_seq    SEQUENCE     �   CREATE SEQUENCE public.player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.player_id_seq;
       public          postgres    false    204    7            6           0    0    player_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.player_id_seq OWNED BY public.player.id;
          public          postgres    false    205            �            1259    25023    status    TABLE     [   CREATE TABLE public.status (
    id integer NOT NULL,
    status_name character varying
);
    DROP TABLE public.status;
       public         heap    postgres    false    7            �            1259    25029    status_id_seq    SEQUENCE     �   CREATE SEQUENCE public.status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.status_id_seq;
       public          postgres    false    206    7            7           0    0    status_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.status_id_seq OWNED BY public.status.id;
          public          postgres    false    207            �
           2604    25091    game id    DEFAULT     b   ALTER TABLE ONLY public.game ALTER COLUMN id SET DEFAULT nextval('public.game_id_seq'::regclass);
 6   ALTER TABLE public.game ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    203    202            �
           2604    25092 	   player id    DEFAULT     f   ALTER TABLE ONLY public.player ALTER COLUMN id SET DEFAULT nextval('public.player_id_seq'::regclass);
 8   ALTER TABLE public.player ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    205    204            �
           2604    25093 	   status id    DEFAULT     f   ALTER TABLE ONLY public.status ALTER COLUMN id SET DEFAULT nextval('public.status_id_seq'::regclass);
 8   ALTER TABLE public.status ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    207    206            (          0    25007    game 
   TABLE DATA           r   COPY public.game (id, sid, board, start_date, end_date, id_player1, id_player2, id_winner, id_status) FROM stdin;
    public          postgres    false    202   �.       *          0    25015    player 
   TABLE DATA           :   COPY public.player (id, sid, login, password) FROM stdin;
    public          postgres    false    204   �0       ,          0    25023    status 
   TABLE DATA           1   COPY public.status (id, status_name) FROM stdin;
    public          postgres    false    206   w2       8           0    0    game_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('public.game_id_seq', 5, true);
          public          postgres    false    203            9           0    0    player_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.player_id_seq', 5, true);
          public          postgres    false    205            :           0    0    status_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.status_id_seq', 1, false);
          public          postgres    false    207            �
           2606    25035    game game_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.game DROP CONSTRAINT game_pkey;
       public            postgres    false    202            �
           2606    25037    player player_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.player DROP CONSTRAINT player_pkey;
       public            postgres    false    204            �
           2606    25039    status status_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.status DROP CONSTRAINT status_pkey;
       public            postgres    false    206            �
           2606    25041    status status_status_name_key 
   CONSTRAINT     _   ALTER TABLE ONLY public.status
    ADD CONSTRAINT status_status_name_key UNIQUE (status_name);
 G   ALTER TABLE ONLY public.status DROP CONSTRAINT status_status_name_key;
       public            postgres    false    206            �
           1259    25042    ix_game_end_date    INDEX     E   CREATE INDEX ix_game_end_date ON public.game USING btree (end_date);
 $   DROP INDEX public.ix_game_end_date;
       public            postgres    false    202            �
           1259    25043 
   ix_game_id    INDEX     9   CREATE INDEX ix_game_id ON public.game USING btree (id);
    DROP INDEX public.ix_game_id;
       public            postgres    false    202            �
           1259    25044    ix_game_id_player1    INDEX     I   CREATE INDEX ix_game_id_player1 ON public.game USING btree (id_player1);
 &   DROP INDEX public.ix_game_id_player1;
       public            postgres    false    202            �
           1259    25045    ix_game_id_player2    INDEX     I   CREATE INDEX ix_game_id_player2 ON public.game USING btree (id_player2);
 &   DROP INDEX public.ix_game_id_player2;
       public            postgres    false    202            �
           1259    25046    ix_game_id_status    INDEX     G   CREATE INDEX ix_game_id_status ON public.game USING btree (id_status);
 %   DROP INDEX public.ix_game_id_status;
       public            postgres    false    202            �
           1259    25047    ix_game_id_winner    INDEX     G   CREATE INDEX ix_game_id_winner ON public.game USING btree (id_winner);
 %   DROP INDEX public.ix_game_id_winner;
       public            postgres    false    202            �
           1259    25048    ix_game_sid    INDEX     B   CREATE UNIQUE INDEX ix_game_sid ON public.game USING btree (sid);
    DROP INDEX public.ix_game_sid;
       public            postgres    false    202            �
           1259    25049    ix_game_start_date    INDEX     I   CREATE INDEX ix_game_start_date ON public.game USING btree (start_date);
 &   DROP INDEX public.ix_game_start_date;
       public            postgres    false    202            �
           1259    25050    ix_player_id    INDEX     =   CREATE INDEX ix_player_id ON public.player USING btree (id);
     DROP INDEX public.ix_player_id;
       public            postgres    false    204            �
           1259    25051    ix_player_login    INDEX     J   CREATE UNIQUE INDEX ix_player_login ON public.player USING btree (login);
 #   DROP INDEX public.ix_player_login;
       public            postgres    false    204            �
           1259    25052    ix_player_password    INDEX     I   CREATE INDEX ix_player_password ON public.player USING btree (password);
 &   DROP INDEX public.ix_player_password;
       public            postgres    false    204            �
           1259    25053    ix_player_sid    INDEX     F   CREATE UNIQUE INDEX ix_player_sid ON public.player USING btree (sid);
 !   DROP INDEX public.ix_player_sid;
       public            postgres    false    204            �
           1259    25054    ix_status_id    INDEX     =   CREATE INDEX ix_status_id ON public.status USING btree (id);
     DROP INDEX public.ix_status_id;
       public            postgres    false    206            �
           2606    25055    game game_id_player1_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_id_player1_fkey FOREIGN KEY (id_player1) REFERENCES public.player(id);
 C   ALTER TABLE ONLY public.game DROP CONSTRAINT game_id_player1_fkey;
       public          postgres    false    204    2720    202            �
           2606    25060    game game_id_player2_fkey    FK CONSTRAINT     |   ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_id_player2_fkey FOREIGN KEY (id_player2) REFERENCES public.player(id);
 C   ALTER TABLE ONLY public.game DROP CONSTRAINT game_id_player2_fkey;
       public          postgres    false    204    202    2720            �
           2606    25065    game game_id_status_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_id_status_fkey FOREIGN KEY (id_status) REFERENCES public.status(id);
 B   ALTER TABLE ONLY public.game DROP CONSTRAINT game_id_status_fkey;
       public          postgres    false    206    2723    202            �
           2606    25070    game game_id_winner_fkey    FK CONSTRAINT     z   ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_id_winner_fkey FOREIGN KEY (id_winner) REFERENCES public.player(id);
 B   ALTER TABLE ONLY public.game DROP CONSTRAINT game_id_winner_fkey;
       public          postgres    false    202    2720    204            (   ;  x��V[�� ��O�z &��d����a�dgm���Sqy&�i�T�6d�hՄ�W<�N��e��f���������}��8������7-8��?�AX?���?�'����sM�(�%Ce�d �B�y��O����B���^|i�+�h����� �`�fT}����ן+6��d����)f?�N�N9����yci��KB�x6��RWm�?Jغ���O���RK�)� .Å�`��T���*�Q�Y:<�hߒoߖ~;��J;���U�H.ti�U��^�s� gכK�]�,���3�B�/;����Ş��`�89�*ȦKA�]6c��oG|I�~t�T8�_(�NK�nLh�/Gseގ���=����D�[cT��b��Mތ������)�����9r�p�GzĎ�!]�x��Sq�(w�ɚϏ�O����8k�}y-m��Ñ��)���{����<z��=�:�4G�Ss�V�-N+\�s�<N	뿟$~agaJC(�t�S1�V؎)����0�Ϗ��j�勊����7��i�@���p˦�M�z�S�`���u��U��      *   �  x�5��m�1�����A���l� HU~.��U�!��T@�a#�7˖��y��M�#��3K�#�������-,�^�k�����0��<sG��It�x�C�4K��]�	� %�Y�t��Y�Y��=OB.�J���o����% H��5��P��Y;�y5lQ�4&g���[(�Xa�y��Ӛ�����g��U�l�B���������t����!�I0΢����Z1�X�OE�/m��$&-���$��������\ת's���hYM�>�]nCMuq`������ZX�vv�"��I��O;ں�*�f�u�g��Y`B�W^V��.<��������x�������/��y��)q�lUF�$k��i�UJh �"�l<�p�t�1�y���ͫ�����M      ,   ;   x�0 ��1	В процессе
2	Завершена
\.


��Q     