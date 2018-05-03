if [ ! -d "/tmp/rmq" ]; then
  echo "creating /tmp/rmq"
  mkdir /tmp/rmq
  mkdir /tmp/rmq/home
  mkdir /tmp/rmq/config
  chmod 777 /tmp/rmq/config
  echo "[rabbitmq_management]." >>/tmp/rmq/config/enabled_plugins
fi

docker run --rm -it \
   -h rmqserver \
   --name server \
   -p 127.0.0.1:15672:15672 \
   -p 127.0.0.1:5672:5672 \
   -v /tmp/rmq/home/:/var/lib/rabbitmq \
   -v /tmp/rmq/config/:/etc/rabbitmq/ \
   rabbitmq:3.7-management
