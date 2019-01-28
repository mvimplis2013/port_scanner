#FROM is the base image for which we will run our application [gttpd, lighttpd, monkey] 
FROM nginx:latest

#COPY files and directories from local filesystem to container
COPY index.html /usr/share/nginx/html
COPY css/ /usr/share/nginx/html/css
COPY ./*.js /usr/share/nginx/html/

# Tell Docker we are going to use this port
EXPOSE 80

# docker build -t deep-sea .
# docker run deep-sea

# Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
# docker tag SOURCE_IMAGE[:tag] TARGET_IMAGE[:tag]

# Tag an image referenced by Name and Tag into fedora repository  
# docker tag httpd fedora/httpd:version1.0

# Eventually upload the image to Docker hub (tag the image with your Docker Hub username)

# Docker Hub login: vibm69/ firewindRRD
# docker login 
# docker push deep-sea vibm69/deep-sea:1.0

# *** Is my container running ? ===> docker ps !
# List of/ Contains deep-sea

# After container is created successfully ... go and run the application
# docker run -d -p 80:80 deep-sea

# Web Browser ---> http://localhost/

# Kill ALL running containers: docker kill $(docker ps -a -q)

# Let docker run the web-application into a randomized port:
# docker run -d -p 80 deep-sea
