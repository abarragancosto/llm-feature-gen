#!/usr/bin/env python3

import argparse, pathlib
from llm_feature_gen.generator import FeatureGenerator

def parse_args():
    ap = argparse.ArgumentParser(
        description="Genera escenarios Gherkin o casos de uso con modelos locales"
    )
    ap.add_argument("requirements", help="Path al archivo de requisitos (txt/md)")
    ap.add_argument("-m","--mockup", help="Imagen mock-up (opcional, para visión)")
    ap.add_argument(
        "-n", "--num", type=int, default=5,
        help="Número de escenarios o casos de uso (default: 5)"
    )
    ap.add_argument(
        "-o", "--output", default="output.feature",
        help="Nombre del archivo de salida (default: output.feature)"
    )
    ap.add_argument(
        "-f","--format", choices=["feature", "txt"], default="feature",
        help="Formato de salida: feature=Gherkin | txt=casos de uso (default: feature)"
    )
    ap.add_argument(
        "--prompt-file", metavar="FILE",
        help="Plantilla de prompt personalizada (opcional)"
    )
    return ap.parse_args()


def main():
    args = parse_args()

    req_text = pathlib.Path(args.requirements).read_text(encoding="utf-8")

    gen = FeatureGenerator()

    ui_desc = None
    if args.mockup:
        print("[Vision] Analizando mock-up ...")
        ui_desc = gen.describe_ui(args.mockup)
        print(ui_desc)

    custom_prompt = (
        pathlib.Path(args.prompt_file).read_text()
        if args.prompt_file else None
    )
    scenarios = gen.generate(req_text, ui_desc, args.num, custom_prompt)

    if args.format == "txt":
        scenarios = (
            scenarios.replace("Feature:", "# Caso de uso:")
                     .replace("Scenario:", "# Escenario:")
        )

    pathlib.Path(args.output).write_text(scenarios, encoding="utf-8")
    print(f"[OK] Archivo generado: {args.output}")


if __name__ == "__main__":
    main()
