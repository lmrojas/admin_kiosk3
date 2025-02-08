# Usar imagen oficial de Nginx
FROM nginx:1.21

# Copiar configuración personalizada
COPY gateway.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Comando por defecto de Nginx
CMD ["nginx", "-g", "daemon off;"] 