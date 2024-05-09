FROM alpine:3.19 as runner

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

# renovate: datasource=github-releases depName=sqldef/sqldef
ENV SQLDEF_VERSION=v0.17.8

# hadolint ignore=DL3018
RUN apk add --no-cache curl && \
  ARCH=$([ "$(uname -m)" = "aarch64" ] && echo "arm64" || echo "amd64") && \
  curl -sSL "https://github.com/sqldef/sqldef/releases/download/${SQLDEF_VERSION}/mysqldef_linux_${ARCH}.tar.gz" | \
  tar -xzC /usr/local/bin && \
  apk del curl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV TZ=Asia/Tokyo

ENTRYPOINT ["/entrypoint.sh"]