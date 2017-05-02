#!/bin/bash
set -ex

if [ -z $NO_DEFAULT ]; then
  OUTPUT="www"
  LIB_COPY="filelist.txt"
  NO_WEB=1
  PUBLISH=
fi

if [ -z $NO_WEB ]; then
  git submodule update --init --recursive
  pip install --upgrade pip
  pip install --upgrade python-dateutil ghp-import pytz
fi

mkdir -p "${OUTPUT}"
find . -not -path '*.git/*' -not -path '*'"${OUTPUT}/"'*' -type f -not -name '*.md' -not -name '*.py' -not -name '*.tmpl' -not -name '*.sh' -not -name "${LIB_COPY}" -not -name '.*' > "${LIB_COPY}"
rsync -av . "${OUTPUT}" --files-from "${LIB_COPY}"
./create_page.py --documents content.json --template index.tmpl --out "${OUTPUT}/index.html"
PREV_DIR=`pwd`
pushd "${OUTPUT}" && find . -not -path '*lib/*' -not -path '*lib' | "${PREV_DIR}/create_sitemap.py" "sitemap.xml" && popd

if [ -z $PUBLISH ]; then
  python -m SimpleHTTPServer || true
  rm -rf "${OUTPUT}"
  rm "${LIB_COPY}"
else
  ghp-import -n "${OUTPUT}" &&
  git push -qf "https://${GH_TOKEN}@github.com/${TRAVIS_REPO_SLUG}.git" gh-pages
fi
