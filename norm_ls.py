#!/usr/bin/env python3
import json
import logging
from subprocess import PIPE, Popen
from sys import stderr

from lsprotocol import types
from pygls import uris
from pygls.cli import start_server
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument


class Hint:
    def __init__(self, code: str, message: str, line: str, char: str) -> None:
        self.code = code
        self.message = message
        self.line = line
        self.char = char

    def __str__(self) -> str:
        return (
            f"[{self.line}:{self.char}]{self.code.capitalize()}"
            f": {self.message}"
        )

    def __repr__(self) -> str:
        return str(self)


def get_hints(file: str) -> list[Hint] | None:
    TIMEOUT: int = 5
    process = Popen(
        [
            "norminette",
            "-d",
            "-R",
            "CheckForbiddenSourceHeader",
            "-f",
            "json",
            file,
        ],
        stdout=PIPE,
    )
    try:
        (output, _) = process.communicate(timeout=TIMEOUT)
        _ = process.wait(timeout=TIMEOUT)
    except Exception as e:
        print(f"Failed to gather hints: {e}", file=stderr)
        process.kill()
    line = output.splitlines()[1]
    if not line:
        return None
    content = json.loads(line)["files"][0]
    status = content["status"]
    errors = content["errors"]
    hints: list[Hint] = []
    if status == "Error":
        for h in errors:
            hints.append(
                Hint(
                    h["name"],
                    h["text"],
                    h["highlights"][0]["lineno"],
                    h["highlights"][0]["column"],
                )
            )
    return hints


class PublishDiagnosticServer(LanguageServer):
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)
        self.diagnostics = {}

    def parse(self, document: TextDocument) -> None:
        if not uris.to_fs_path(document.uri):
            return
        else:
            file = str(uris.to_fs_path(document.uri))
        hints = get_hints(file)
        diagnostics = []
        if hints:
            for hint in hints:
                diagnostics.append(
                    types.Diagnostic(
                        message=hint.message,
                        code=hint.code,
                        code_description=None,
                        severity=types.DiagnosticSeverity(value=1),
                        source="norm_ls",
                        range=types.Range(
                            start=types.Position(
                                line=int(hint.line) - 1,
                                character=int(hint.char) - 1,
                            ),
                            end=types.Position(
                                line=int(hint.line) - 1,
                                character=int(hint.char) - 1,
                            ),
                        ),
                    )
                )
        self.diagnostics[document.uri] = (document.version, diagnostics)


server = PublishDiagnosticServer(
    "norm_ls",
    "v0.1.3",
    text_document_sync_kind=types.TextDocumentSyncKind(1),
)


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(
    ls: PublishDiagnosticServer, params: types.DidOpenTextDocumentParams
) -> None:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=version,
                diagnostics=diagnostics,
            )
        )


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(
    ls: PublishDiagnosticServer, params: types.DidChangeTextDocumentParams
) -> None:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=version,
                diagnostics=diagnostics,
            )
        )


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
def did_save(
    ls: PublishDiagnosticServer, params: types.DidSaveTextDocumentParams
) -> None:
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)

    for uri, (version, diagnostics) in ls.diagnostics.items():
        ls.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri,
                version=version,
                diagnostics=diagnostics,
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
