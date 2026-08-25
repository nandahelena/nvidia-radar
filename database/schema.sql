CREATE TABLE startups (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    site VARCHAR(300),
    setor VARCHAR(100),
    estagio VARCHAR(50),
    localizacao VARCHAR(150),
    descricao_curta TEXT,
    ano_fundacao INTEGER,
    tamanho_time INTEGER
);

CREATE TABLE documentos (
    id SERIAL PRIMARY KEY,
    startup_id INTEGER NOT NULL REFERENCES startups(id) ON DELETE CASCADE,
    tipo VARCHAR(50),
    titulo VARCHAR(300),
    conteudo_texto TEXT NOT NULL,
    url_fonte VARCHAR(500),
    data_publicacao DATE
);

CREATE INDEX idx_documentos_startup_id ON documentos(startup_id);