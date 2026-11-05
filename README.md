# DOCUMENTO INICIAL BASE PARA IMPLEMENTAÇÃO DO PROJETO

## Visão geral

O sistema atual deve ser uma api Django Rest Framework que será consumida num site de chá de bebê.

## Referência para gerar o schema.

A seguir, a estrutura de banco de dados planejada.

### Users

#### fields

uuid, name, login, password

#### seeder

- Gabriel Barroso Faustino Gomes, papai, paissword240227
- Beatriz de Oliveira Figueiredo Gomes, mamae, maessword240227

### Guests

#### fields

uuid, name, age (faixa etária, enum, aceita os valores 'adult' ou 'kid'), phone (opcional, telefone no formato '(99) 9 9999-9999'), confirmed (boolean, criado como false, alterado mediante evento confirmPresence), category (enum, aceita os valores 'family', 'friend', 'church').

#### relationships

- belongsTo invite
- manyToMany gifts

#### Events

- confirmPresence (o usuário confirma sua presença, o que muda o confirmed de false para true)

### invite

#### fields

uuid, name, code (string aleatória de 6 dígitos)

#### relationships

- hasMany guests

#### Events

- confirmGuests (recebe uma lista com todos os integrantes do convite para confirmar presença, dispara guests.confirmPresence para cada um)

### Gifts

#### fields

uuid, name, description, link (url válido), limit (número inteiro positivo, não pode ser menor do que a quantidade de guests_gifts já cadastrados no sistema para aquele gift).

#### relationships

- manyToMany guests
- manyToMany tags (quando criar um gift, envia o campo tag, se não houver tag com o nome igual ao da tag (os dois em uppercase), o sistema cria a tag e o relacionamento automaticamente)
- hasMany files (várias imagens associadas a ele)

### Tags

#### fields

uuid, name (unique, uppercase), description

#### relationships

- manyToMany gifts

### files

#### fields

uuid, name (unique), alt

#### relationships

- belongsTo Gifts
