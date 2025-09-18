#!/bin/sh
# scripts/minio-bootstrap.sh
set -eu

log() { printf "%s %s\n" "[minio-init]" "$*"; }

# Vars requeridas
: "${MINIO_ROOT_USER:?MINIO_ROOT_USER requerido}"
: "${MINIO_ROOT_PASSWORD:?MINIO_ROOT_PASSWORD requerido}"
: "${S3_BUCKET:?S3_BUCKET requerido}"

# Opcionales para usuario/keys
: "${N8N_USER:=}"
: "${N8N_PASSWORD:=}"
: "${N8N_ACCESS_KEY:=}"
: "${N8N_SECRET_KEY:=}"

ALIAS_NAME="local"
ENDPOINT="http://minio:9000"

log "Esperando a MinIO en ${ENDPOINT}..."
i=1
while [ "$i" -le 60 ]; do
  if mc alias set "$ALIAS_NAME" "$ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; then
    log "Alias ${ALIAS_NAME} OK"
    break
  fi
  log "MinIO no listo aún (${i}/60)..."
  i=$((i+1))
  sleep 2
done

# Intento final (si falla, aborta)
mc alias set "$ALIAS_NAME" "$ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
log "Conexión establecida"

# Bucket idempotente
if mc ls "${ALIAS_NAME}/${S3_BUCKET}" >/dev/null 2>&1; then
  log "Bucket ya existe: ${S3_BUCKET}"
else
  mc mb -p "${ALIAS_NAME}/${S3_BUCKET}"
  log "Bucket creado: ${S3_BUCKET}"
fi

# --------- ILM: expirar a 7 días (evitar duplicados sin grep) ---------
ILM_OUT="$(mc ilm rule ls "${ALIAS_NAME}/${S3_BUCKET}" 2>/dev/null || true)"
case "$ILM_OUT" in
  *"Expiration"*)
    log "Regla ILM ya existe (no se crea otra)"
    ;;
  *)
    mc ilm rule add --expire-days 7 "${ALIAS_NAME}/${S3_BUCKET}"
    log "Regla ILM (7 días) creada"
    ;;
esac
mc ilm rule ls "${ALIAS_NAME}/${S3_BUCKET}" || true


# Usuario/Política/Access Key (si se definieron todas)
if [ -n "${N8N_USER}" ] && [ -n "${N8N_PASSWORD}" ] && [ -n "${N8N_ACCESS_KEY}" ] && [ -n "${N8N_SECRET_KEY}" ]; then
  POLICY_NAME="${S3_BUCKET}-rw"
  POLICY_FILE="/tmp/${POLICY_NAME}.json"

  if ! mc admin policy info "$ALIAS_NAME" "$POLICY_NAME" >/dev/null 2>&1; then
    cat >"$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["s3:ListAllMyBuckets"], "Resource": ["*"] },
    { "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::raw-data"] },
    { "Effect": "Allow", "Action": ["s3:GetObject","s3:PutObject","s3:DeleteObject"], "Resource": ["arn:aws:s3:::raw-data/*"] }
  ]
}
EOF
mc admin policy create local raw-data-rw /tmp/raw-data-rw.json
mc admin policy attach local raw-data-rw --user n8n_user
mc admin accesskey info local/ n8n_user_access || true
log "Política creada: ${POLICY_NAME}"
  else
    log "Política ya existe: ${POLICY_NAME}"
  fi

  if ! mc admin user info "$ALIAS_NAME" "$N8N_USER" >/dev/null 2>&1; then
    mc admin user add "$ALIAS_NAME" "$N8N_USER" "$N8N_PASSWORD"
    log "Usuario creado: ${N8N_USER}"
  else
    log "Usuario ya existe: ${N8N_USER}"
  fi

  mc admin policy attach "$ALIAS_NAME" "$POLICY_NAME" --user "$N8N_USER" || true
  log "Política ${POLICY_NAME} adjunta a ${N8N_USER}"

  if ! mc admin accesskey info "${ALIAS_NAME}/" "$N8N_ACCESS_KEY" >/dev/null 2>&1; then
    mc admin accesskey create "${ALIAS_NAME}/" "$N8N_USER" \
      --access-key "$N8N_ACCESS_KEY" \
      --secret-key "$N8N_SECRET_KEY" \
      --description "n8n acceso a ${S3_BUCKET}" \
      --expiry-duration 365d
    log "Access key creada: ${N8N_ACCESS_KEY}"
  else
    log "Access key ya existe: ${N8N_ACCESS_KEY}"
  fi
else
  log "Saltando creación de usuario/keys (variables no provistas)"
fi

log "Bootstrap MinIO COMPLETADO"
