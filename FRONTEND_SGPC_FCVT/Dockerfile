# ETAPA 1: Construcción (Node.js)
FROM node:18-alpine AS build
WORKDIR /app

# Copiamos package.json e instalamos dependencias
COPY package*.json ./
RUN npm install

# Copiamos el resto del código y compilamos para producción
COPY . .
RUN npm run build

# ETAPA 2: Servidor Web (Nginx)
FROM nginx:alpine

# Copiamos los archivos compilados de Vue a la carpeta pública de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiamos nuestra configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto 80 (HTTP)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]