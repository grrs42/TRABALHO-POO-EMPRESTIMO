-- Exemplares fictícios para demonstração do protótipo.
-- Executar após os seeds de grupos e tipos.

INSERT INTO public.materiais (
    codigo,
    numero,
    tipo_id,
    grupo_id,
    disponivel,
    marca,
    modelo,
    tamanho,
    titulo,
    editora,
    descricao
)
SELECT
    dados.codigo,
    dados.numero,
    t.id,
    g.id,
    TRUE,
    dados.marca,
    dados.modelo,
    dados.tamanho,
    dados.titulo,
    dados.editora,
    dados.descricao
FROM (
    VALUES
        ('JAL-001', 1, 'JAL', 'Marca X',
         NULL, 'M', NULL, NULL, NULL),

        ('LIV-001', 1, 'LIV', NULL,
         NULL, NULL, 'POO em Python', 'Editora Teste', NULL),

        ('CAL-001', 1, 'CAL', 'Marca Y',
         'C-100', NULL, NULL, NULL, NULL),

        ('REG-001', 1, 'REG', NULL,
         NULL, NULL, NULL, NULL, 'Régua de 30 cm')
) AS dados (
    codigo, numero, sigla, marca,
    modelo, tamanho, titulo, editora, descricao
)
JOIN public.tipos_material t
    ON t.sigla = dados.sigla
JOIN public.grupos_responsaveis g
    ON g.codigo = 'GEES'
ON CONFLICT (codigo) DO NOTHING;