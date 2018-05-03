#!/bin/bash

DOCKERFILE=Dockerfile
SCRIPTDIR=$(dirname $(realpath $0))

# simple sanity check
if [ ! -e "$SCRIPTDIR/$DOCKERFILE" ]; then
  echo "hmm... can't find my Dockerfile - something wrong?"
else
  echo "building from: $SCRIPTDIR"
fi

# pack up Python code
cd $SCRIPTDIR/..; find * -name "*.py" -print |sort |tar cjvf $SCRIPTDIR/pack.tar.bz2 -T -
cd $SCRIPTDIR


# and build image
IMAGE="cogitator:latest"
docker rmi $IMAGE

echo ""
echo "===== building latest"

docker build --no-cache -f $SCRIPTDIR/$DOCKERFILE -t $IMAGE .

echo ""
echo "===== ...done!"
