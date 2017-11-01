###################################################
# Base Image: base_ubuntu_TBD_ntp_nginx 
#--------------------------------------------------
# Purpose: 
# Debug NGINX
#
#--------------------------------------------------
# Last Revision: 10/08/2016 
###################################################

# Parent Image - Maually align with data/active_container_ver when a new version is created
FROM base_ubuntu_1604_ntp_nginx 
MAINTAINER suppport@greenarmada.org 

# Special bash shell handling required by Unbuntu 
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Run as user
USER root

# Set environment variables
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Internal Port
EXPOSE 443

# Initialize Env
ADD startNtpNginx /root/startNtpNginx
RUN chmod 777 /root/startNtpNginx

# Command to execute upon entry
ENTRYPOINT ["/root/startNtpNginx"]

