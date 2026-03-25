# Nginx for serving static files and proxying to Django
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our config
COPY nginx.conf /etc/nginx/conf.d/

# Create directories for static/media files
RUN mkdir -p /workspace/staticfiles /workspace/media

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]