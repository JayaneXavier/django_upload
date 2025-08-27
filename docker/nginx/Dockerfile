FROM nginx:1.27-alpine
RUN mkdir -p /vol/static /vol/media && chown -R nginx:nginx /vol
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
