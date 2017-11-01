###################################################
# Base Image: ent_TBD_anaconda 
#--------------------------------------------------
# Purpose: 
# Docker Listen for Python Control Panel (PROD)
#
#--------------------------------------------------
# Last Revision: 10/08/2016
###################################################

# Parent Image
FROM ### INSERT: ENTANACONDA 
MAINTAINER support@greenarmada.org 

# Special bash shell handling required by Unbuntu 
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Run as user
USER root

# Set environment variables
ENV PATH /root/anaconda3:/root/anaconda3/envs:/root/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Build Dependencies
ADD enterprise_admin.yml /root/enterprise_admin.yml
RUN chmod 755 /root/enterprise_admin.yml
RUN conda env create -f /root/enterprise_admin.yml
ADD ent_console /root/ent_console
RUN chmod 755 /root/ent_console
ADD ent_console.py /root/ent_console.py
RUN chmod 755 /root/ent_console.py
ADD admin_utils.py /root/admin_utils.py
RUN chmod 755 /root/admin_utils.py

# Internal Port
EXPOSE 10100

# Command to execute upon entry
ENTRYPOINT ["/root/ent_console"]

