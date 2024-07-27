#!/bin/bash
apt update
apt install python3-pip -y
apt install python3-venv -y
apt install awscli -y
apt install nginx -y
apt install unzip -y

cd /home/ubuntu
git clone https://github.com/dvdg6566/codebreaker-contest-manager
cd codebreaker-contest-manager

python3 -m venv virtualenv
source virtualenv/bin/activate
pip3 install -r requirements.txt

mkdir config
mkdir /home/ubuntu/.aws/

{
  echo '[default]'
  echo 'region = ${AWS::Region}'
  echo 'output = json'
} >> config/awsconfig
cp config/awsconfig /home/ubuntu/.aws/config

touch .env
{
  echo 'JUDGE_NAME = ${JudgeName}'
  echo 'AWS_ACCOUNT_ID = ${AWS::AccountId}'
  echo 'AWS_REGION = ${AWS::Region}'
  echo ''
  echo 'TIMEZONE_OFFSET = 8'
  echo 'COGNITO_CLIENT_ID = ${UserPoolClient}'
  echo 'COGNITO_USER_POOL_ID = ${UserPool}'
  echo 'API_GATEWAY_LINK = wss://${WebSocket}.execute-api.ap-southeast-1.amazonaws.com/production'
  echo 'FLASK_SECRET_KEY = sometemporaryplaceholder'
} >> .env

mkdir /home/ubuntu/codebreaker-contest-manager/static/cppreference
cd /home/ubuntu/codebreaker-contest-manager/static/cppreference
wget https://upload.cppreference.com/mwiki/images/b/b2/html_book_20190607.zip -O cppreference.zip
unzip cppreference.zip
rm cppreference.zip

cp init/systemd /etc/systemd/system/codebreaker.service
cp init/nginx /etc/nginx/sites-available/default

systemctl start codebreaker
systemctl enable codebreaker
systemctl start nginx
systemctl restart nginx
systemctl enable nginx