INSERT INTO public.tipos_material
    (sigla, nome, especializacao)
VALUES
    ('JAL', 'Jaleco', 'JALECO'),
    ('LIV', 'Livro', 'LIVRO'),
    ('CAL', 'Calculadora', 'CALCULADORA'),
    ('REG', 'Régua', 'OUTRO')
ON CONFLICT (sigla) DO NOTHING;