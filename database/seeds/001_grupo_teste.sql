INSERT INTO public.grupos_responsaveis (codigo, nome)
VALUES ('GEES', 'Grêmio de Engenharia de Sistemas')
ON CONFLICT (codigo) DO NOTHING;