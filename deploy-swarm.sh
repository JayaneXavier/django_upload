#!/bin/bash

# Script para deploy da aplicação Django no Docker Swarm
# Demonstra escala horizontal e balanceamento de carga

echo "=== Django Upload - Deploy Docker Swarm ==="

# Verifica se está no modo Swarm
if ! docker info | grep -q "Swarm: active"; then
    echo "Inicializando Docker Swarm..."
    docker swarm init
fi

# Cria a rede overlay se não existir
echo "Criando rede overlay..."
docker network create --driver overlay --attachable app_network 2>/dev/null || echo "Rede já existe"

# Remove stack anterior se existir
echo "Removendo stack anterior (se existir)..."
docker stack rm django-upload 2>/dev/null || true

# Aguarda remoção completa
echo "Aguardando limpeza completa..."
sleep 10

# Deploy da nova stack
echo "Fazendo deploy da stack..."
docker stack deploy -c docker-compose.swarm.yml django-upload

echo ""
echo "=== Status do Deploy ==="
docker stack services django-upload

echo ""
echo "=== Aguardando serviços ficarem prontos ==="
sleep 15

echo ""
echo "=== Status Final ==="
docker stack services django-upload

echo ""
echo "=== Informações de Acesso ==="
echo "Frontend (aplicação web): http://localhost:8080"
echo "Frontend Info (JSON): http://localhost:8080/frontend-info/"
echo "Backend API: http://localhost:8080/api/backend-info/"
echo "Portainer: http://localhost:9000"

echo ""
echo "=== Comandos úteis ==="
echo "Ver logs do frontend: docker service logs django-upload_frontend"
echo "Ver logs do backend: docker service logs django-upload_backend"
echo "Escalar frontend: docker service scale django-upload_frontend=5"
echo "Escalar backend: docker service scale django-upload_backend=5"
echo "Ver status: docker stack services django-upload"
echo "Remover stack: docker stack rm django-upload"