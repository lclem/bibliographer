#!/bin/bash

NAME="${1}"
NEW_NAME="${NAME//:/_}"

echo "MV ${NAME} => ${NEW_NAME}"
git mv ${NAME} ${NEW_NAME}
#echo DONE
