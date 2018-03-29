#!/bin/bash

echo ""
use_doc_theme="alabaster"
if [[ "${DOC_THEME}" != "" ]]; then
    use_doc_theme="${DOC_THEME}"
else
    export DOC_THEME=${use_doc_theme}
fi

if [[ ! -e ./staticfiles ]]; then
    mkdir -p -m 775 ./staticfiles
fi

echo "Making HTML Documentation with theme: ${use_doc_theme}"
doc_path=drf_network_pipeline/docs
cd $doc_path
make html
cd ../..

echo ""
echo "Fixing static url links for Django"
fix_these_files=$(find drf_network_pipeline/docs/build/html -name "*.html" | grep -v "/rest_framework_swagger/")
for html in $fix_these_files; do
    echo "fixing ${html}"
    sed -i 's|src="_static|src="/static|g' $html
    sed -i 's|href="_static|href="/static|g' $html
    sed -i 's|href="_images|href="/static/_images|g' $html
    sed -i 's|href="_sources|href="/static/_sources|g' $html
    sed -i 's|href="_downloads|href="/static/_downloads|g' $html
done

echo ""
echo "Fixing static url for one-off cases"
sed -i 's|/static/_sources/index.rst.txt|/docs/_sources/index.rst.txt|' drf_network_pipeline/docs/build/html/index.html

exit 0
