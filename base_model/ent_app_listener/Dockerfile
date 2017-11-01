###################################################
# Base Image: ent_TBD_anaconda 
#--------------------------------------------------
# Purpose: 
# Docker Listen for Python HTTPS Service Requests
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
ADD creds.json /root/creds.json
RUN chmod 755 /root/creds.json
ADD active_anaconda_env.yml /root/active_anaconda_env.yml
RUN chmod 755 /root/active_anaconda_env.yml
RUN conda env create -f /root/active_anaconda_env.yml

# Internal Port
### INSERT: PORT

# Command to execute upon entry
ENTRYPOINT ["/shared_volume/scripts/### INSERT: SCRIPTWRAPPER"]

