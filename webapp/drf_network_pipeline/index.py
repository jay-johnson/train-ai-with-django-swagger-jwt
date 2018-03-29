from django.conf import settings
from django.shortcuts import render


def handle_sphinx_doc_index(
        request,
        data=None):
    """handle_sphinx_doc_index

    Generic handler for sending the browser to the
    sphinx documentation index:

    <repo>/webapp/drf_network_pipeline/docs/build/html/index.html

    :param request: HTTPRequest
    :param data: extra data
    """
    return render(
        request,
        settings.DEFAULT_DOC_INDEX_HTML)
# end of handle_sphinx_doc_index
