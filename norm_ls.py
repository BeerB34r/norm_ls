import re
import logging
from pygls.lsp.server import LanguageServer
from pygls.cli import start_server
from pygls.workspace import TextDocument
from pygls import uris
from lsprotocol import types
from subprocess import Popen, PIPE

class Hint:
    def __init__(self, code, message, line, char):
        self.code = code
        self.message = message
        self.line = line
        self.char = char

def get_hints(file: str):
    process = Popen(["norminette", "-d", file], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    lines = output.splitlines()
    if not lines:
        return None
    hints = []
    for i in lines:
        if str(i).find("Error:") > 0:
            hints.append(Hint(re.search("[A-Z_]+$", re.search("Error:\s[A-Z_]+", str(i)).group(0)).group(0),
                              str(i).split(':').pop()[2:-1],
                              re.search("[0-9]+", re.search("line:\s*[0-9]+", str(i)).group(0)).group(0),
                              re.search("[0-9]+", re.search("col:\s*[0-9]+", str(i)).group(0)).group(0)))
    return hints

class PublishDiagnosticServer(LanguageServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diagnostics = {}

    def parse(self, document: TextDocument):
        hints = get_hints(uris.to_fs_path(document.uri))
        diagnostics = []
        if hints:
            for hint in hints:
                diagnostics.append(
                        types.Diagnostic(
                            message = hint.message,
                            code = hint.code,
                            code_description = None,
                            severity = types.DiagnosticSeverity(value = 1),
                            source = "norm_ls",
                            range = types.Range(
                                start = types.Position(line = int(hint.line) - 1, character = int(hint.char) - 1),
                                end = types.Position(line = int(hint.line) - 1, character = int(hint.char) - 1)
                                )))
        self.diagnostics[document.uri] = (document.version, diagnostics)

server = PublishDiagnosticServer("norm_ls", "v0.1.2", text_document_sync_kind = types.TextDocumentSyncKind(1),)

@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: PublishDiagnosticServer, params: types.DidOpenTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri = uri,
                    version = version,
                    diagnostics = diagnostics,
                    )
                )

@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: PublishDiagnosticServer, params: types.DidChangeTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri = uri,
                    version = version,
                    diagnostics = diagnostics,
                    )
                )

@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: PublishDiagnosticServer, params: types.DidSaveTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
                types.PublishDiagnosticsParams(
                    uri = uri,
                    version = version,
                    diagnostics = diagnostics,
                    )
                )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
