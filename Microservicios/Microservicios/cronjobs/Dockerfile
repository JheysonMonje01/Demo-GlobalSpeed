FROM alpine:latest

RUN apk --no-cache add curl bash

COPY verificar_cron /etc/crontabs/root
COPY verificar_vencimientos.sh /app/verificar_vencimientos.sh

RUN chmod +x /app/verificar_vencimientos.sh
RUN mkdir -p /var/log

CMD ["crond", "-f", "-l", "8"]
