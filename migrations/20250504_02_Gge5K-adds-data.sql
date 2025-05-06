-- adds data
-- depends: 20250504_01_MprBc-initial

INSERT INTO public.channel (channel, title, "default")
VALUES 
    ('general', 'General Channel', true),
    ('technical', 'Technical Support', false)
ON CONFLICT (channel) DO NOTHING;

