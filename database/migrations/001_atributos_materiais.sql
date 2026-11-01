BEGIN;

-- Especialização associada ao tipo de material.
ALTER TABLE public.tipos_material
ADD COLUMN IF NOT EXISTS especializacao VARCHAR(20)
    NOT NULL DEFAULT 'OUTRO';

-- Atributos comuns e específicos dos materiais.
ALTER TABLE public.materiais
    ADD COLUMN IF NOT EXISTS marca VARCHAR(100),
    ADD COLUMN IF NOT EXISTS modelo VARCHAR(100),
    ADD COLUMN IF NOT EXISTS tamanho VARCHAR(10),
    ADD COLUMN IF NOT EXISTS titulo VARCHAR(200),
    ADD COLUMN IF NOT EXISTS editora VARCHAR(120),
    ADD COLUMN IF NOT EXISTS descricao TEXT;

-- Restringe os valores aceitos para especialização.
ALTER TABLE public.tipos_material
ADD CONSTRAINT tipos_material_especializacao_check
CHECK (
    especializacao IN (
        'CALCULADORA',
        'JALECO',
        'LIVRO',
        'OUTRO'
    )
);

COMMIT;