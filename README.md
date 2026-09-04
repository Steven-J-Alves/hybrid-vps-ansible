# hybrid-vps-ansible

Ansible playbook + roles que configuram o **lado VPS** da arquitetura híbrida:
- **Tailscale** — install + join tailnet, aceitar rotas da VPC AWS
- **ECS Anywhere agent** — registar VPS como container instance no cluster `hybrid-apis` (consome outputs de `hybrid-networking-terraform/ecs-anywhere-activation/`)
- **Traefik multi-network** — reconciliar `/home/claw/companies/kriolu-kloud.cv/traefik/docker-compose.yml` para incluir a network `bridge` (para descobrir tasks ECS Anywhere)

## Convenções

| Item | Valor |
|---|---|
| Inventory host | `openclaw` (alias em `~/.ssh/config`, ver `../../../../../../vps-access`) |
| Connection | SSH via `ssh openclaw` (porta 52222, user `claw`, key `~/.ssh/claw_vps`) |
| Ansible Python interpreter | `/usr/bin/python3` |
| Roles | `roles/{tailscale,ecs-anywhere,traefik-multinet}/tasks/main.yml` |

## Ponte Terraform → Ansible

```bash
# Depois de terraform apply em hybrid-networking-terraform
cd ../hybrid-networking-terraform/ecs-anywhere-activation
terraform output -json > /tmp/tf-outputs.json

# Correr playbook (extra vars vêm do TF)
cd ../../hybrid-vps-ansible
ansible-playbook -i inventory playbook.yaml -e "@/tmp/tf-outputs.json"
```

Outputs consumidos:
- `ssm_activation_id` (secret)
- `ssm_activation_code` (secret)
- `ecs_cluster_name` (`p-hybrid-apis` ou `h-hybrid-apis`)
- `aws_region` (`us-east-1`)
- `tailscale_auth_key` (secret, reusable)

## Ordem de execução dos roles

1. **`tailscale`** — install + `tailscale up --accept-routes`. Sem isto, VPS não chega a ElastiCache/Aurora.
2. **`ecs-anywhere`** — install script + `--cluster $ECS_CLUSTER --activation-id ... --activation-code ...`. VPS aparece em `aws ecs list-container-instances`.
3. **`traefik-multinet`** — editar (ou reescrever) o compose do Traefik existente adicionando `bridge` à network list, restart. Cuidado: playbook é idempotente e verifica se a alteração já está aplicada antes de restart.

## Correr

```bash
ansible-playbook -i inventory playbook.yaml
# Ou uma tag específica:
ansible-playbook -i inventory playbook.yaml --tags tailscale
```

## Isolamento

Este playbook **não toca** em:
- Containers existentes na network `traefik-public` (bussola, gitlab, mailcow, documind, etc.)
- Config do Mailcow em `/opt/mailcow-dockerized/`
- Config global do Docker daemon (`/etc/docker/daemon.json`)

Só o compose do Traefik é editado (com backup automático antes).

## Status

**Skeleton** — inventory e playbook.yaml preparados, roles com `tasks/main.yml` placeholder. A preencher nas Fases 1 (tailscale), 5 (ecs-anywhere + traefik-multinet).
