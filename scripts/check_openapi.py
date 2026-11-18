#!/usr/bin/env python3
"""Compara o OpenAPI gerado pelo Consolidator com contracts/openapi.yaml.

Uso:
    python scripts/check_openapi.py            # compara; sai 0 se igual, 1 se divergir
    python scripts/check_openapi.py --update   # grava o gerado em contracts/openapi.yaml

Se já houver um Consolidator respondendo em --url, ele é usado. Caso contrário,
o script sobe o Consolidator no perfil dev (H2 em memória, BRAPI_TOKEN fictício),
baixa /v3/api-docs.yaml e derruba a aplicação ao final.

Saídas: 0 = contrato igual ao código; 1 = divergência (diff impresso);
2 = erro de infraestrutura (não subiu, timeout, arquivo ausente).
Só usa a biblioteca padrão.
"""
from __future__ import annotations

import argparse
import difflib
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = HUB / "contracts" / "openapi.yaml"
DEFAULT_CONSOLIDATOR = HUB.parent / "consolidator" / "consolidator"
DOCS_PATH = "/v3/api-docs.yaml"


def fetch(url: str, timeout: float = 5.0) -> str | None:
    try:
        with urllib.request.urlopen(url + DOCS_PATH, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
        return None


def start_consolidator(project_dir: Path, log_path: Path) -> subprocess.Popen:
    mvnw = project_dir / ("mvnw.cmd" if os.name == "nt" else "mvnw")
    if not mvnw.exists():
        raise FileNotFoundError(f"mvnw não encontrado em {project_dir}")
    env = dict(os.environ)
    env.setdefault("BRAPI_TOKEN", "check-openapi-dummy")
    if os.name == "nt":
        # mvnw.cmd chama o powershell; em shells como o Git Bash ele pode não estar no PATH.
        root = env.get("SystemRoot", r"C:\Windows")
        ps_dir = str(Path(root) / "System32" / "WindowsPowerShell" / "v1.0")
        env["PATH"] = ps_dir + os.pathsep + str(Path(root) / "System32") + os.pathsep + env.get("PATH", "")
    log = open(log_path, "w", encoding="utf-8")
    kwargs: dict = {}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(
        [str(mvnw), "-q", "spring-boot:run"],
        cwd=project_dir,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        **kwargs,
    )


def stop(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
        subprocess.run([str(taskkill), "/T", "/F", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()


def normalize(text: str) -> list[str]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip() for line in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:8080")
    parser.add_argument("--consolidator-dir", type=Path, default=DEFAULT_CONSOLIDATOR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--timeout", type=int, default=240, help="segundos para o Consolidator subir")
    parser.add_argument("--update", action="store_true", help="grava o gerado no contrato em vez de comparar")
    args = parser.parse_args()

    generated = fetch(args.url)
    proc = None
    if generated is None:
        log_path = HUB / "scripts" / ".check-openapi.log"
        print(f"Nenhum Consolidator em {args.url}; subindo em {args.consolidator_dir} (log: {log_path})")
        try:
            proc = start_consolidator(args.consolidator_dir, log_path)
        except FileNotFoundError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2
        deadline = time.time() + args.timeout
        try:
            while time.time() < deadline:
                if proc.poll() is not None:
                    print(f"ERRO: o Consolidator encerrou antes de responder. Veja {log_path}", file=sys.stderr)
                    return 2
                generated = fetch(args.url)
                if generated is not None:
                    break
                time.sleep(3)
            else:
                print(f"ERRO: timeout de {args.timeout}s esperando {args.url}{DOCS_PATH}", file=sys.stderr)
                return 2
        finally:
            stop(proc)
    else:
        print(f"Usando o Consolidator que já está em {args.url}")

    if args.update:
        args.contract.parent.mkdir(parents=True, exist_ok=True)
        args.contract.write_text("\n".join(normalize(generated)) + "\n", encoding="utf-8", newline="\n")
        print(f"Contrato atualizado: {args.contract}")
        return 0

    if not args.contract.exists():
        print(f"ERRO: contrato não encontrado: {args.contract}", file=sys.stderr)
        return 2

    expected = normalize(args.contract.read_text(encoding="utf-8"))
    actual = normalize(generated)
    if expected == actual:
        print(f"OK: o código bate com {args.contract.name} ({len(actual)} linhas)")
        return 0

    diff = difflib.unified_diff(expected, actual, fromfile=f"contrato ({args.contract.name})",
                                tofile="gerado pelo código", lineterm="", n=2)
    print("\n".join(diff))
    print(f"\nDIVERGÊNCIA: o código não bate com {args.contract}. Atualize o contrato "
          "(contrato primeiro) ou corrija o código.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
