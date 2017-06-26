FROM centos:6.8
MAINTAINER <adam@cluebyfour.ca>

RUN yum -y update && rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm && yum -y install sudo python-pip python-devel gcc libffi libffi-devel openssl-devel && yum clean all
RUN mkdir /deploy
COPY . /deploy/
WORKDIR /deploy
RUN pip install -r requirements.txt 

VOLUME /deploy/ssh_keys

CMD ["./bot.py"]
