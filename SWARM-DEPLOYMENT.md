# Django Upload - Docker Swarm com Réplicas e Balanceamento

## Visão Geral da Arquitetura

Este projeto demonstra uma aplicação Django deployada em Docker Swarm com:

- **Frontend**: Nginx + Django (3 réplicas) - porta 8080
- **Backend**: Django API (3 réplicas) - comunicação interna
- **Database**: PostgreSQL (1 réplica) - dados persistentes
- **Portainer**: Interface de gerenciamento (porta 9000)
- **Rede Overlay**: Comunicação segura entre serviços

## Topologia dos Serviços

```
Internet -> Frontend (nginx:8080) -> Backend (django:8000) -> Database (postgres:5432)
   │              │                        │
   │              └─ 3 réplicas             └─ 3 réplicas  
   │                                        
   └─ Portainer (9000)
```

## Modificações Realizadas

### 1. Portas Alteradas
- **Antes**: Porta 80
- **Depois**: Porta 8080 (para evitar conflitos)

**Por que**: Muitos desenvolvedores já usam a porta 80 para outros projetos. A porta 8080 é uma alternativa comum que evita conflitos.

### 2. Endpoints de Monitoramento
Adicionei endpoints para demonstrar o balanceamento:

- `/frontend-info/`: Mostra qual réplica do frontend atendeu
- `/api/backend-info/`: Mostra qual réplica do backend atendeu

### 3. Arquitetura Frontend/Backend
- **Frontend**: Serve interface web e faz proxy para backend
- **Backend**: API pura que responde com informações da instância
- **Comunicação**: Frontend → Backend via rede overlay

## Pré-requisitos

1. Docker instalado
2. Docker Compose instalado  
3. Git Bash ou terminal Unix (Windows)
4. Imagens Docker construídas:
   - `nome_da_imagem:tag` (Django)
   - `nome_da_imagem_nginx:tag` (Nginx)
   -  docker build -t django-upload-nginx:latest -f docker/nginx/Dockerfile .
   -  docker build -t django-upload:latest -f docker/web/Dockerfile .


## Deploy Passo a Passo

### 1. Inicializar Docker Swarm

```bash
# Inicializa o Swarm (se ainda não estiver ativo)
docker swarm init
```

### 2. Criar Rede Overlay

```bash
# Cria rede para comunicação entre serviços
docker network create --driver overlay --attachable my_overlay_network
```

### 3. Deploy da Stack

```bash
# Deploy usando o arquivo de configuração do Swarm
docker stack deploy -c docker-compose.yml django-upload
```

### 4. Verificar Status

```bash
# Verifica se todos os serviços estão rodando
docker stack services django-upload
```

## Scripts Automatizados

### Deploy Automático
```bash
# Torna executável e roda
chmod +x deploy-swarm.sh
./deploy-swarm.sh
```

### Teste de Balanceamento
```bash
# Testa alternância entre réplicas
chmod +x test-load-balancing.sh
./test-load-balancing.sh
```

## Testando o Balanceamento

### 1. Teste Manual via Navegador
```
http://localhost:8080/frontend-info/
```
Recarregue várias vezes - observe mudanças no `frontend_container_id` e `backend_container_id`

### 2. Teste via Linha de Comando
```bash
# Frontend
for i in {1..10}; do curl -s http://localhost:8080/frontend-info/ | jq '.frontend_container_id'; done
FOR /L %i IN (1,1,10) DO curl -s http://localhost:8080/frontend-info/

# Backend  
for i in {1..10}; do curl -s http://localhost:8080/api/backend-info/ | jq '.backend_container_id'; done
```
FOR /L %i IN (1,1,10) DO curl -s http://localhost:8080/api/backend-info/
FOR /L %i IN (1,1,10) DO curl -s http://localhost:8080/frontend-info/


### 3. Teste de Comunicação Interna
```bash
# Verifica como frontend chama backend
curl -s http://localhost:8080/frontend-info/ | jq '.'
```

## Escalonamento Dinâmico

### Aumentar Réplicas
```bash
# Escala frontend para 5 réplicas
docker service scale django-upload_frontend=5

# Escala backend para 5 réplicas  
docker service scale django-upload_backend=5
```

### Diminuir Réplicas
```bash
# Reduz para 2 réplicas
docker service scale django-upload_frontend=2 django-upload_backend=2
```

### Verificar Mudanças
```bash
# Ve o status após escalonamento
docker stack services django-upload
```

## Monitoramento e Logs

### Logs dos Serviços
```bash
# Frontend
docker service logs django-upload_frontend

# Backend
docker service logs django-upload_backend

# Database
docker service logs django-upload_db
```

### Portainer (Interface Visual)
```
http://localhost:9000
```

### Status Detalhado
```bash
# Lista todas as tasks/containers
docker stack ps django-upload

# Info detalhada de um serviço
docker service inspect django-upload_frontend
```

## Lista container para recuperar ID
docker ps --filter "name=django-upload_frontend"

## Testando Resiliência

### 1. Simular Falha de Container
```bash
# Remove um container específico
docker container rm -f $(docker ps | grep django-upload_frontend | head -1 | awk '{print $1}')
docker container rm -f ID_DO_CONTAINER_COPIADO

# Swarm automaticamente cria uma nova réplica
```

### 2. Update Rolling
```bash
# Atualiza imagem com rolling update
docker service update --image nova_imagem:tag django-upload_frontend
```

### 3. Teste Durante Update
```bash
# Executa requisições durante o update
while true; do curl -s http://localhost:8080/frontend-info/ | jq '.frontend_container_id'; sleep 1; done
```

## Limpeza

### Remover Stack
```bash
docker stack rm django-upload
```

### Remover Rede
```bash
docker network rm app_network
```

### Sair do Swarm (opcional)
```bash
docker swarm leave --force
```

## Explicação Técnica

### Por que Docker Swarm?

1. **Balanceamento Automático**: Distribui requisições entre réplicas automaticamente
2. **Service Discovery**: Serviços se encontram por nome (ex: `backend`)
3. **Rede Overlay**: Comunicação segura e isolada entre serviços
4. **Self-Healing**: Recria containers que falham automaticamente
5. **Rolling Updates**: Atualizações sem downtime

### Como Funciona o Balanceamento?

1. **Frontend Load Balancer**: Nginx distribui requisições HTTP entre réplicas Django
2. **Swarm Load Balancer**: Docker distribui conexões entre containers do mesmo serviço
3. **Round Robin**: Algoritmo padrão alterna entre réplicas disponíveis
4. **Health Checks**: Remove réplicas não saudáveis do pool

### Rede Overlay Explicada

- **Isolamento**: Tráfego entre serviços é isolado do host
- **Criptografia**: Comunicação criptografada por padrão
- **Multi-Host**: Funciona mesmo com múltiplos Docker hosts
- **DNS Interno**: Resolução de nomes automática (`backend` → IP das réplicas)

## Troubleshooting

### Problema: Serviço não sobe
```bash
# Verifica logs
docker service logs django-upload_frontend

# Verifica constraints
docker service inspect django-upload_frontend
```

### Problema: Não consegue conectar ao backend
```bash
# Testa conectividade na rede
docker run --rm --network app_network alpine ping backend
```

### Problema: Porta já em uso
```bash
# Verifica quem está usando a porta
netstat -tulpn | grep 8080

# Mata processo se necessário
sudo lsof -t -i:8080 | xargs kill -9
```