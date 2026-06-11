1. Front-end:
    - O front-end deve possibilitar que o usuário realize consultas sobre informações provenientes da API da NASA;
    - Exemplo: buscar informações sobre imagens astronômicas do dia, meteoritos, foguetes, missões, etc;
    - Não há limitação de framework ou linguagem. Pode ser puro HTML/CSS/JS, React, Flutter Web, Angular, etc.
 
2. Back-end (API FastAPI):
    - Você deverá desenvolver uma API utilizando FastAPI (Python);
    - A API será responsável por:
    - Consumir todos os endpoints GET disponíveis na API da NASA;
    - Servir de intermediário entre o front-end e a API da NASA;
    - Não é permitido o front-end acessar diretamente a API da NASA: toda comunicação deve passar pelo back-end FastAPI desenvolvido pela equipe.
 
3. API da NASA:
    - Documentação: Clique aqui!
    - Implemente todos os endpoints das rotas GET disponíveis;
    - Ao menos um exemplo de consumo de cada endpoint GET deve existir no back-end de vocês.
 
4. Restrições:
    - Não é necessário implementar autenticação/autorização de usuários;
    - NÃO é necessário implementar métodos POST, PUT, DELETE (apenas GET);
    - A API FastAPI não deve armazenar os dados consumidos, apenas repassar os dados aos clientes (frontend).
 
5. Critérios de avaliação:
- Documentação;
- Organização, legibilidade e modularização do código-fonte;
- Performance da aplicação;
- Tratamento de erros e respostas inválidas;
- Uso de Vibe Coding;
- Boas práticas de desenvolvimento.
