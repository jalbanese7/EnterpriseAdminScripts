###################################################
# Base Image: ent_TBD_anaconda 
#--------------------------------------------------
# Purpose: 
# Docker Batch Luigi Task Handler
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
ENV PATH .:/root:/root/anaconda3:/root/anaconda3/envs:/root/anaconda3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
ENV PYTHONPATH=/shared_volume/python_codebase

# Internal Port
EXPOSE 9999 

# Build Dependencies
RUN apt-get install -y vim
ADD creds.json /root/creds.json
ADD go_batch /root/go_batch
ADD go_listener /root/go_listener
ADD go_env /root/go_env
ADD go_test /root/go_test
ADD go_conda /root/go_conda
ADD go_setclock /root/go_setclock
RUN chmod 755 /root/creds.json
RUN chmod 755 /root/go_batch
RUN chmod 755 /root/go_listener
RUN chmod 755 /root/go_test
RUN chmod 755 /root/go_conda
RUN chmod 755 /root/go_setclock

# Command to execute upon entry
ENTRYPOINT ["/bin/bash"]

