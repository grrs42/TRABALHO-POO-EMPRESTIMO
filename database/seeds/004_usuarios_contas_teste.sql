INSERT INTO public.usuarios (matricula, nome)
VALUES ('2026000001', 'Estudante Teste')
ON CONFLICT (matricula) DO NOTHING;

INSERT INTO public.grupos_responsaveis (codigo, nome)
VALUES ('LABFIS', 'Laboratório de Física')
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO public.contas_acesso
    (login, senha_hash, salt, tipo, usuario_matricula, grupo_codigo)
VALUES
    ('2026000001',
     '6efa1948e39b8468b3d6c8d25deac90fb272ee3313f8b9b14c8cfd1d1e6fd4b3',
     'c89366ac61f0a7699b7e830ef20ff153',
     'ESTUDANTE', '2026000001', NULL),
    ('GEES',
     '5fd1bca7ace09f4652adc76163ba043b4f1ca95668672536c649b0b695f43fdc',
     'f80c2ace86dfc01aa595ae90ed2c4c19',
     'GRUPO', NULL, 'GEES'),
    ('LABFIS',
     'e43ce983a6179195cd767e1a1caaddcb330bd5696448c3fdfedef259a98545b4',
     '59216b12b5c4f36a5fef7855f67308d7',
     'GRUPO', NULL, 'LABFIS')
ON CONFLICT (login) DO NOTHING;
