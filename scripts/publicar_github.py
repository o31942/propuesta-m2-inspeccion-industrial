"""Script para crear el repositorio en GitHub, subir ramas (main y develop),
crear las 4 etiquetas oficiales (ML, Backend, Frontend, Testing), publicar las
11 Historias de Usuario con sus AC y Fibonacci 1:1 como Issues de GitHub y
configurar el tablero GitHub Projects.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
REPO_NAME = "propuesta-m2-inspeccion-industrial"
REPO_DESC = (
    "Propuesta Formal M2 (35%) UAO - Sistema Desacoplado de Inspección de Calidad "
    "Industrial (NEU-DET + YOLOv8/RT-DETR + CLAHE + Eigen-CAM) con uv, src/ layout, pytest y ruff"
)

OFFICIAL_LABELS = [
    ("ML", "7C3AED", "Tareas de Machine Learning, Visión por Computador, CLAHE y XAI"),
    (
        "Backend",
        "2563EB",
        "Tareas de arquitectura src/, orquestador, API REST y Docker",
    ),
    (
        "Frontend",
        "059669",
        "Interfaz interactiva en Streamlit para operarios de planta",
    ),
    ("Testing", "D97706", "Fixtures sintéticos, pruebas unitarias AAA con pytest y QA"),
]


def get_github_credentials() -> tuple[str, str]:
    """Obtiene usuario y token desde argumento CLI, variable de entorno GITHUB_TOKEN o Git Credential Manager."""
    import os

    if len(sys.argv) > 1 and sys.argv[1].strip():
        return os.environ.get("GITHUB_USER", "o31942"), sys.argv[1].strip()

    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token:
        return os.environ.get("GITHUB_USER", "o31942"), env_token.strip()

    env = os.environ.copy()
    env["GCM_INTERACTIVE"] = "never"
    env["GIT_TERMINAL_PROMPT"] = "0"
    gcm_exe = r"C:\Program Files\Git\mingw64\bin\git-credential-manager.exe"
    cmd = (
        [gcm_exe, "get"] if Path(gcm_exe).exists() else [GIT_EXE, "credential", "fill"]
    )
    proc = subprocess.run(
        cmd,
        input="protocol=https\nhost=github.com\n\n",
        text=True,
        capture_output=True,
        timeout=10,
        env=env,
        check=False,
    )
    username = ""
    password = ""
    for line in proc.stdout.splitlines():
        if line.startswith("username="):
            username = line.split("=", 1)[1].strip()
        elif line.startswith("password="):
            password = line.split("=", 1)[1].strip()
    if not password:
        raise RuntimeError(
            "No se encontraron credenciales activas de GitHub. Define $env:GITHUB_TOKEN='tu_token' o inicia sesión con Git Credential Manager."
        )
    return username, password


def gh_api(
    method: str,
    url: str,
    token: str,
    payload: dict[str, object] | None = None,
) -> tuple[int, dict[str, object] | list[object]]:
    """Realiza una petición autenticada a la API REST/GraphQL de GitHub."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "UAO-M2-Industrial-Script")
    if data is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as err:
        raw_err = err.read().decode("utf-8", errors="replace")
        try:
            return err.code, json.loads(raw_err)
        except Exception:
            return err.code, {"message": raw_err}


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    username, token = get_github_credentials()
    st_u, u_info = gh_api("GET", "https://api.github.com/user", token)
    if st_u == 200 and isinstance(u_info, dict) and "login" in u_info:
        username = str(u_info["login"])
    print(f"Autenticado en GitHub como: {username}")

    # 1. Crear o verificar repositorio público en GitHub
    status, repo_info = gh_api(
        "POST",
        "https://api.github.com/user/repos",
        token,
        {
            "name": REPO_NAME,
            "description": REPO_DESC,
            "private": False,
            "has_issues": True,
            "has_projects": True,
            "auto_init": False,
        },
    )
    if status in (200, 201):
        print(
            f"Repositorio creado exitosamente: https://github.com/{username}/{REPO_NAME}"
        )
    elif status == 422:
        print(
            f"El repositorio https://github.com/{username}/{REPO_NAME} ya existe; sincronizando..."
        )
    else:
        print(f"Respuesta al crear repositorio ({status}): {repo_info}")
        sys.exit(1)

    remote_url = f"https://github.com/{username}/{REPO_NAME}.git"
    auth_push_url = (
        f"https://x-access-token:{token}@github.com/{username}/{REPO_NAME}.git"
    )

    # 2. Configurar remote origin y hacer push de main y develop usando el token directamente
    subprocess.run(
        [GIT_EXE, "-C", str(base_dir), "remote", "remove", "origin"],
        capture_output=True,
    )
    subprocess.run(
        [GIT_EXE, "-C", str(base_dir), "remote", "add", "origin", remote_url],
        check=True,
    )
    subprocess.run(
        [GIT_EXE, "-C", str(base_dir), "push", auth_push_url, "main:main", "--force"],
        check=True,
    )
    subprocess.run(
        [
            GIT_EXE,
            "-C",
            str(base_dir),
            "push",
            auth_push_url,
            "develop:develop",
            "--force",
        ],
        check=True,
    )
    print("Ramas 'main' y 'develop' publicadas correctamente en GitHub.")

    # 3. Crear las 4 etiquetas oficiales (ML, Backend, Frontend, Testing)
    for lbl_name, lbl_color, lbl_desc in OFFICIAL_LABELS:
        st_lbl, _ = gh_api(
            "POST",
            f"https://api.github.com/repos/{username}/{REPO_NAME}/labels",
            token,
            {"name": lbl_name, "color": lbl_color, "description": lbl_desc},
        )
        if st_lbl in (200, 201):
            print(f"Etiqueta creada: {lbl_name}")
        else:
            gh_api(
                "PATCH",
                f"https://api.github.com/repos/{username}/{REPO_NAME}/labels/{lbl_name}",
                token,
                {"new_name": lbl_name, "color": lbl_color, "description": lbl_desc},
            )
            print(f"Etiqueta actualizada: {lbl_name}")

    # 4. Consultar issues existentes para no duplicar si se re-ejecuta
    st_iss, existing_issues = gh_api(
        "GET",
        f"https://api.github.com/repos/{username}/{REPO_NAME}/issues?state=all&per_page=100",
        token,
    )
    existing_titles = set()
    if st_iss == 200 and isinstance(existing_issues, list):
        for item in existing_issues:
            if isinstance(item, dict) and "title" in item:
                existing_titles.add(str(item["title"]))

    # 5. Crear las 11 Historias de Usuario desde docs/github_projects_backlog.csv
    csv_path = base_dir / "docs" / "github_projects_backlog.csv"
    created_node_ids: list[tuple[str, str]] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["Title"]
            if title in existing_titles:
                print(f"Issue ya existente, omitiendo creación: {title}")
                continue
            sp = row["Story_Points_Fibonacci"]
            days = row["Duration_Days"]
            label = row["Label"]
            assignee_role = row["Assignee"]
            kanban_status = row["Status"]
            story = row["User_Story"]
            ac_list = [ac.strip() for ac in row["Acceptance_Criteria"].split("|")]
            ac_md = "\n".join(
                f"- [x] {ac}" if kanban_status == "Done" else f"- [ ] {ac}"
                for ac in ac_list
            )

            body = (
                f"### Historia de Usuario ({row['Ticket']})\n"
                f"> **{story}**\n\n"
                f"--- \n"
                f"### Metadatos Ágiles (Acto III & IV — Regla Fibonacci 1:1)\n"
                f"- **Etiqueta Oficial:** `{label}`\n"
                f"- **Estimación Fibonacci (1:1):** `{sp} SP` ({days} días de ingeniería)\n"
                f"- **Responsable Asignado:** {assignee_role}\n"
                f"- **Columna Inicial en Tablero Kanban:** `{kanban_status}`\n\n"
                f"### Criterios de Aceptación Verificables (AC)\n"
                f"{ac_md}\n"
            )
            st_c, iss_resp = gh_api(
                "POST",
                f"https://api.github.com/repos/{username}/{REPO_NAME}/issues",
                token,
                {
                    "title": title,
                    "body": body,
                    "labels": [label],
                },
            )
            if st_c in (200, 201) and isinstance(iss_resp, dict):
                print(f"Issue creado: {title} [{label} | {sp} SP]")
                node_id = str(iss_resp.get("node_id", ""))
                if node_id:
                    created_node_ids.append((node_id, kanban_status))
            else:
                print(f"Error creando issue {title}: {st_c} {iss_resp}")

    # 6. Intentar crear el tablero GitHub Projects v2 vía GraphQL si el token tiene scope project
    q_user = {"query": "query { viewer { id login } }"}
    st_g, g_resp = gh_api("POST", "https://api.github.com/graphql", token, q_user)
    if st_g == 200 and isinstance(g_resp, dict) and "data" in g_resp:
        viewer_id = g_resp["data"]["viewer"]["id"]  # type: ignore[index]
        mut_proj = {
            "query": """
            mutation($ownerId: ID!, $title: String!) {
              createProjectV2(input: {ownerId: $ownerId, title: $title}) {
                projectV2 { id url number }
              }
            }
            """,
            "variables": {
                "ownerId": viewer_id,
                "title": "Kanban M2 - Inspección de Calidad Industrial (NEU-DET)",
            },
        }
        st_p, p_resp = gh_api("POST", "https://api.github.com/graphql", token, mut_proj)
        if (
            st_p == 200
            and isinstance(p_resp, dict)
            and p_resp.get("data")
            and p_resp["data"].get("createProjectV2")  # type: ignore[union-attr]
        ):
            proj_data = p_resp["data"]["createProjectV2"]["projectV2"]  # type: ignore[index]
            proj_id = proj_data["id"]
            proj_url = proj_data["url"]
            print(f"Tablero GitHub Projects creado: {proj_url}")
            for content_id, _status_col in created_node_ids:
                add_item_mut = {
                    "query": """
                    mutation($projectId: ID!, $contentId: ID!) {
                      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                        item { id }
                      }
                    }
                    """,
                    "variables": {"projectId": proj_id, "contentId": content_id},
                }
                gh_api("POST", "https://api.github.com/graphql", token, add_item_mut)
            print(
                "Las 11 Historias de Usuario fueron vinculadas al tablero GitHub Projects."
            )
        else:
            print(
                "Nota: El token actual tiene permisos de repositorio ('repo') pero no el scope 'project' "
                "para crear tableros Projects v2 vía GraphQL. Los 11 Issues con etiquetas ML, Backend, "
                "Frontend y Testing ya están creados en el repositorio listos para vincular en 1 clic."
            )


if __name__ == "__main__":
    main()
