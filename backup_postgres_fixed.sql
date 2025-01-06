-- Desabilitar chaves estrangeiras temporariamente
SET session_replication_role = 'replica';

BEGIN TRANSACTION;

-- 1. django_content_type
CREATE TABLE IF NOT EXISTS "django_content_type" (
    "id" SERIAL PRIMARY KEY,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL,
    UNIQUE ("app_label", "model")
);

-- 2. auth_permission
CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id" SERIAL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename" varchar(100) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);

-- 3. auth_group
CREATE TABLE IF NOT EXISTS "auth_group" (
    "id" SERIAL PRIMARY KEY,
    "name" varchar(150) NOT NULL UNIQUE
);

-- 4. auth_group_permissions
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id" SERIAL PRIMARY KEY,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
);

-- 5. auth_user
CREATE TABLE IF NOT EXISTS "auth_user" (
    "id" SERIAL PRIMARY KEY,
    "password" varchar(128) NOT NULL,
    "last_login" timestamp NULL,
    "is_superuser" boolean NOT NULL,
    "username" varchar(150) NOT NULL UNIQUE,
    "first_name" varchar(150) NOT NULL,
    "last_name" varchar(150) NOT NULL,
    "email" varchar(254) NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "date_joined" timestamp NOT NULL
);

-- 6. auth_user_groups
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
);

-- 7. auth_user_user_permissions
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
);

-- 8. django_admin_log
CREATE TABLE IF NOT EXISTS "django_admin_log" (
    "id" SERIAL PRIMARY KEY,
    "action_time" timestamp NOT NULL,
    "object_id" text NULL,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint NOT NULL CHECK ("action_flag" >= 0),
    "change_message" text NOT NULL,
    "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- 9. django_session
CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key" varchar(40) PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" timestamp NOT NULL
);

-- 10. Índices
CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE INDEX IF NOT EXISTS "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");

-- 11. Outras Tabelas Específicas
CREATE TABLE IF NOT EXISTS "guardiao_categoria" (
    "id" SERIAL PRIMARY KEY,
    "nome" varchar(100) NOT NULL UNIQUE,
    "descricao" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_assinante" (
    "id" SERIAL PRIMARY KEY,
    "nome" varchar(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_funcaoassinante" (
    "id" SERIAL PRIMARY KEY,
    "nome" varchar(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_prontoarmamento" (
    "id" SERIAL PRIMARY KEY,
    "data" date NOT NULL,
    "numero" integer NOT NULL UNIQUE CHECK ("numero" >= 0),
    "lacre" varchar(50) NOT NULL,
    "assinante_1_id" integer NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "assinante_2_id" integer NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "assinante_3_id" integer NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_1_id" integer NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_2_id" integer NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_3_id" integer NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tabela" text NOT NULL
);


CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id" SERIAL PRIMARY KEY,
    "content_type_id" INTEGER NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename" VARCHAR(100) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    UNIQUE ("content_type_id", "codename")
);


CREATE TABLE IF NOT EXISTS "auth_group" (
    "id" SERIAL PRIMARY KEY,
    "name" varchar(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id" SERIAL PRIMARY KEY,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id")
);

CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
);

CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
);

-- Índices
CREATE INDEX IF NOT EXISTS "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX IF NOT EXISTS "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE INDEX IF NOT EXISTS "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX IF NOT EXISTS "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
CREATE TABLE IF NOT EXISTS "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);

CREATE INDEX IF NOT EXISTS "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");

CREATE TABLE IF NOT EXISTS "django_admin_log" (
    "id" SERIAL PRIMARY KEY,
    "object_id" text NULL,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0),
    "change_message" text NOT NULL,
    "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "action_time" datetime NOT NULL
);

CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE TABLE IF NOT EXISTS "guardiao_emprestimo" (
    "id" SERIAL PRIMARY KEY,
    "destino" varchar(200) NOT NULL,
    "data_emprestimo" datetime NOT NULL,
    "data_devolucao" datetime NULL,
    "cliente_id" bigint NOT NULL REFERENCES "guardiao_cliente" ("id") DEFERRABLE INITIALLY DEFERRED,
    "operador_id" bigint NOT NULL REFERENCES "guardiao_operador" ("id") DEFERRABLE INITIALLY DEFERRED,
    "isAtiva" bool NOT NULL
);

CREATE INDEX IF NOT EXISTS "guardiao_emprestimo_cliente_id_7946aba1" ON "guardiao_emprestimo" ("cliente_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimo_operador_id_7fe128f0" ON "guardiao_emprestimo" ("operador_id");

CREATE TABLE IF NOT EXISTS "guardiao_emprestimomaterial" (
    "id" SERIAL PRIMARY KEY,
    "quantidade" integer unsigned NOT NULL CHECK ("quantidade" >= 0),
    "emprestimo_id" bigint NOT NULL REFERENCES "guardiao_emprestimo" ("id") DEFERRABLE INITIALLY DEFERRED,
    "material_id" bigint NOT NULL REFERENCES "guardiao_material" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "guardiao_emprestimomaterial_emprestimo_id_95e473ad" ON "guardiao_emprestimomaterial" ("emprestimo_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimomaterial_material_id_44e78a17" ON "guardiao_emprestimomaterial" ("material_id");

CREATE TABLE IF NOT EXISTS "guardiao_material" (
    "id" SERIAL PRIMARY KEY,
    "nome" varchar(100) NOT NULL,
    "registro" varchar(50) NULL UNIQUE,
    "categoria_id" bigint NULL REFERENCES "guardiao_categoria" ("id") DEFERRABLE INITIALLY DEFERRED,
    "quantidade_disponivel" integer unsigned NOT NULL CHECK ("quantidade_disponivel" >= 0),
    "quantidade_emprestada" integer unsigned NOT NULL CHECK ("quantidade_emprestada" >= 0),
    "quantidade_total" integer unsigned NOT NULL CHECK ("quantidade_total" >= 0)
);

CREATE INDEX IF NOT EXISTS "guardiao_material_categoria_id_1b517172" ON "guardiao_material" ("categoria_id");
CREATE TABLE IF NOT EXISTS "guardiao_emprestimohistorico" (
    "id" SERIAL PRIMARY KEY,
    "status" varchar(50) NOT NULL,
    "data" datetime NOT NULL,
    "emprestimo_id" bigint NOT NULL REFERENCES "guardiao_emprestimo" ("id") DEFERRABLE INITIALLY DEFERRED,
    "operador_id" bigint NULL REFERENCES "guardiao_operador" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX IF NOT EXISTS "guardiao_emprestimohistorico_emprestimo_id_5169d591" ON "guardiao_emprestimohistorico" ("emprestimo_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimohistorico_operador_id_74eb0054" ON "guardiao_emprestimohistorico" ("operador_id");

CREATE TABLE IF NOT EXISTS "guardiao_categoria" (
    "id" SERIAL PRIMARY KEY,
    "nome" varchar(100) NOT NULL UNIQUE,
    "descricao" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_case" (
    "id" SERIAL PRIMARY KEY,
    "descricao" varchar(255) NOT NULL,
    "responsavel" varchar(100) NOT NULL,
    "lacre" varchar(50) NOT NULL UNIQUE,
    "data_criacao" datetime NOT NULL,
    "data_atualizacao" datetime NOT NULL
);
CREATE TABLE IF NOT EXISTS "guardiao_assinante" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" varchar(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_funcaoassinante" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" varchar(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS "guardiao_prontoarmamento" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "data" date NOT NULL,
    "numero" integer unsigned NOT NULL UNIQUE CHECK ("numero" >= 0),
    "lacre" varchar(50) NOT NULL,
    "assinante_1_id" bigint NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "assinante_2_id" bigint NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "assinante_3_id" bigint NOT NULL REFERENCES "guardiao_assinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_1_id" bigint NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_2_id" bigint NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "funcao_3_id" bigint NOT NULL REFERENCES "guardiao_funcaoassinante" ("id") DEFERRABLE INITIALLY DEFERRED,
    "tabela" text NOT NULL
);

CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_assinante_1_id_40a0e205" ON "guardiao_prontoarmamento" ("assinante_1_id");
CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_assinante_2_id_32420624" ON "guardiao_prontoarmamento" ("assinante_2_id");
CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_assinante_3_id_9f823a43" ON "guardiao_prontoarmamento" ("assinante_3_id");
CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_funcao_1_id_84902af6" ON "guardiao_prontoarmamento" ("funcao_1_id");
CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_funcao_2_id_d583fd6b" ON "guardiao_prontoarmamento" ("funcao_2_id");
CREATE INDEX IF NOT EXISTS "guardiao_prontoarmamento_funcao_3_id_3c4a4939" ON "guardiao_prontoarmamento" ("funcao_3_id");
-- Sequências para controle de auto incremento
INSERT INTO sqlite_sequence VALUES('django_migrations', 36);
INSERT INTO sqlite_sequence VALUES('django_admin_log', 158);
INSERT INTO sqlite_sequence VALUES('django_content_type', 17);
INSERT INTO sqlite_sequence VALUES('auth_permission', 68);
INSERT INTO sqlite_sequence VALUES('auth_group', 0);
INSERT INTO sqlite_sequence VALUES('auth_user', 4);
INSERT INTO sqlite_sequence VALUES('guardiao_emprestimo', 42);
INSERT INTO sqlite_sequence VALUES('guardiao_emprestimomaterial', 61);
INSERT INTO sqlite_sequence VALUES('guardiao_categoria', 4);
INSERT INTO sqlite_sequence VALUES('guardiao_emprestimohistorico', 34);
INSERT INTO sqlite_sequence VALUES('guardiao_cliente', 3);
INSERT INTO sqlite_sequence VALUES('guardiao_operador', 3);
INSERT INTO sqlite_sequence VALUES('guardiao_material', 15);
INSERT INTO sqlite_sequence VALUES('guardiao_case', 3);
INSERT INTO sqlite_sequence VALUES('guardiao_funcaoassinante', 4);
INSERT INTO sqlite_sequence VALUES('guardiao_assinante', 4);
INSERT INTO sqlite_sequence VALUES('guardiao_prontoarmamento', 20);

-- Índices adicionais
CREATE INDEX IF NOT EXISTS "guardiao_emprestimomaterial_emprestimo_id_95e473ad" ON "guardiao_emprestimomaterial" ("emprestimo_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimomaterial_material_id_44e78a17" ON "guardiao_emprestimomaterial" ("material_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimo_cliente_id_7946aba1" ON "guardiao_emprestimo" ("cliente_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimo_operador_id_7fe128f0" ON "guardiao_emprestimo" ("operador_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimohistorico_emprestimo_id_5169d591" ON "guardiao_emprestimohistorico" ("emprestimo_id");
CREATE INDEX IF NOT EXISTS "guardiao_emprestimohistorico_operador_id_74eb0054" ON "guardiao_emprestimohistorico" ("operador_id");
CREATE INDEX IF NOT EXISTS "guardiao_material_categoria_id_1b517172" ON "guardiao_material" ("categoria_id");
