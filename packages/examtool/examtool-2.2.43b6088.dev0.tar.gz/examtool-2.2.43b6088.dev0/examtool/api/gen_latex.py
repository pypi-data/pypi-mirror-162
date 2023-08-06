import base64
import hashlib
import os
import os.path
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

from examtool.api.scramble import latex_escape
from examtool.api.watermarks import create_watermark
from examtool.api.utils import rel_path
from examtool.api.assemble_export import OptionQuestion, TextQuestion


def generate(exam, *, include_watermark, prefix, suffix, response=None):
    prefix = prefix or rel_path("tex/prefix.tex")
    suffix = suffix or rel_path("tex/suffix.tex")
    out = []

    def write(x, *, newline=True):
        out.append(x)
        if newline:
            out.append("\n")

    response_lookup = (
        {question.id: question for question in response.questions} if response else {}
    )

    def write_group(group, is_public):
        if is_public:
            if group["points"] is not None:
                write(rf"{{\bf\item ({group['points']} points)\quad}}")
            else:
                write(r"\item[]", newline=False)
        else:
            if group["points"] is not None:
                write(fr"\q{{{group['points']}}}")
            else:
                write(r"\item", newline=False)
        write(r"{ \bf " + latex_escape(group["name"]) + "}")
        write("\n")
        write(group["tex"])
        write(r"\begin{enumerate}[font=\bfseries]")
        for element in group["elements"]:
            if element["type"] == "group":
                write_group(element, False)
            else:
                write_question(element)
        write(r"\end{enumerate}")
        write(r"\clearpage")

    def write_question(question):
        write(r"\filbreak")
        if question["points"] is not None:
            write(fr"\subq{{{question['points']}}}")
        else:
            write(r"\item \, \hspace{-1em} \, ")
        write(question["tex"])

        question_response = response_lookup.get(question["id"])
        solution = question.get("solution", {})
        solution_text = (solution.get("solution", {}) or {}).get("tex", "")
        solution_options = solution.get("options") or []
        template_text = question.get("template", "")

        answer_text = ""
        use_verbatim_answer = False
        wrap_with_solution = False
        if template_text:
            # Add a new line before any "blanks", e.g `return _______`
            answer_text = re.sub(r"(.*(?=___).*)", r"\n\1", template_text)
            answer_text = (
                answer_text.replace("  ", r"\hphantom{XX}")
                .replace(
                    "\t", r"\hphantom{XXXX}"
                )  # Deal with weird lack of indentation
                .replace(r"/$\n/", "")
                .replace("_", r"\_")
                .replace("\n", r" \\ ")
                .replace("%", r"\%")
            )
            num_lines = answer_text.count(r"\\") // 2 + 1
            question["options"] = question["options"] or num_lines
            use_verbatim_answer = True
        if question_response and isinstance(question_response, TextQuestion):
            answer_text = re.sub(r"_{4,}", "\ \ ", question_response.response)
            answer_text = (
                answer_text.replace("_", r"\_")
                .replace("  ", r"\hphantom{XX}")
                .replace("\n", r" \\ ")
                .replace("%", r"\%")
            )
            use_verbatim_answer = True
        elif solution_text:
            answer_text = solution_text
            if "verbatim" in solution_text:
                answer_text = (
                    answer_text.replace("\\begin{verbatim}", "")
                    .replace("\\end{verbatim}", "")
                    .strip()
                )
                use_verbatim_answer = True
            wrap_with_solution = True
        if use_verbatim_answer:
            answer_text = rf"\texttt{{{answer_text}}}"
        if wrap_with_solution:
            answer_text = rf"\solution{{{answer_text}}}"

        if question["type"] in ["short_answer", "short_code_answer"]:
            write(
                rf"\framebox[0.8\textwidth][c]{{\parbox[c][30px]{{0.75\textwidth}}{{{answer_text}}}}}"
            )
        elif question["type"] in ["long_answer", "long_code_answer"]:
            height = 30 * question["options"]
            answer_height = answer_text.count(r"\\") * 10
            if answer_height > height:
                answer_text = rf"\begin{{fitbox}}{{{height}px}}{{0.75\textwidth}}{answer_text}\end{{fitbox}}"
            write(
                rf"\framebox[0.8\textwidth][c]{{\parbox[c][{height}px][t]{{0.75\textwidth}}{{{answer_text}}}}}"
            )

        answer_options = []
        if question_response and isinstance(question_response, OptionQuestion):
            answer_options = [option.text for option in question_response.selected]
        elif solution_options:
            answer_options = solution_options

        if question["type"] in ["select_all"]:
            write(r"\begin{options}")
            for option in question["options"]:
                if option["text"] in answer_options:
                    write(r"\option[\moqs] " + option["tex"])
                else:
                    write(r"\option[\moqb] " + option["tex"])
            write(r"\end{options}")
        if question["type"] in ["multiple_choice"]:
            write(r"\begin{choices}")
            for option in question["options"]:
                if option["text"] in answer_options:
                    write(r"\option[\mcqs] " + option["tex"])
                else:
                    write(r"\option[\mcqb] " + option["tex"])
            write(r"\end{choices}")
        if solution.get("note"):
            write(r"\\\\ \note{")
            write(solution["note"]["tex"])
            write(r"}")
        write(r"\vspace{10px}")

    if include_watermark:
        write(r"\let\Watermarks=1")

    with open(prefix) as f:
        write(f.read())
    for i, group in enumerate(
        ([exam["public"]] if exam["public"] else []) + exam["groups"]
    ):
        is_public = bool(i == 0 and exam["public"])
        write_group(group, is_public)

    with open(suffix) as f:
        write(f.read())

    return "".join(out)


@contextmanager
def render_latex(
    exam,
    subs=None,
    *,
    do_twice=False,
    prefix=None,
    suffix=None,
    suppress_output=False,
    response=None,
):
    include_watermark = exam.get("watermark") and "value" in exam["watermark"]
    tempdir = tempfile.mkdtemp()

    # Generate LaTeX.
    latex = generate(
        exam,
        include_watermark=include_watermark,
        prefix=prefix,
        suffix=suffix,
        response=response,
    )

    # Rewrite HTTP(S) URLs.
    latex = re.sub(
        r"\\includegraphics(\[.*\])?{(http.*/(.+))}",
        r"\\immediate\\write18{wget -N \2}\n\\includegraphics\1{\3}",
        latex,
    )

    # Rewrite data URIs.
    while True:
        match = re.search(
            r"\\includegraphics(\[.*\])?\{(data:((?!;base64)[^,])*(;base64)?,([^}]+))\}",
            latex,
            flags=re.IGNORECASE,
        )
        if not match:
            break

        opt_args = match.group(1) or ""
        data_uri = match.group(2)
        data_type = match.group(3)
        data_base64 = bool(match.group(4))
        data = match.group(5)

        # Generate filename as the hash of the regex match.
        filename = hashlib.sha256(match.group(0).encode()).digest().hex()
        if data_type.lower().startswith("image/png"):
            filename += ".png"
        elif data_type.lower().startswith("image/jpeg"):
            filename += ".jpg"
        else:
            # It"s fine if the data isn't actually a PDF. LaTeX just looks for
            # any data with the extension when doing \includegraphics.
            filename += ".pdf"

        # Decode base64 data.
        if data_base64:
            data_bytes = base64.b64decode(data)
        else:
            data_bytes = data.encode()

        # Write data to filesystem.
        with open(os.path.join(tempdir, filename), "bw") as f:
            f.write(data_bytes)

        latex = latex.replace(
            f"\\includegraphics{opt_args}{{{data_uri}}}",
            f"\\includegraphics{opt_args}{{{filename}}}",
        )

    if subs:
        for k, v in subs.items():
            latex = latex.replace(f"<{k.upper()}>", v)
    with open(f"{tempdir}/out.tex", "w+") as f:
        f.write(latex)

    if include_watermark:
        with open(f"{tempdir}/watermark.svg", "w+") as f:
            f.write(
                create_watermark(
                    exam["watermark"]["value"],
                    brightness=exam["watermark"]["brightness"],
                )
            )
        subprocess.run(
            f'inkscape {tempdir}/watermark.svg -D --export-type="pdf" --export-filename={tempdir}/watermark.pdf',
            shell=True,
        ).check_returncode()

    subprocess.run(
        f"cd {tempdir} && pdflatex --shell-escape -interaction=nonstopmode out.tex",
        shell=True,
        capture_output=suppress_output,
    )
    if do_twice:
        subprocess.run(
            f"cd {tempdir} && pdflatex --shell-escape -interaction=nonstopmode out.tex",
            shell=True,
            capture_output=suppress_output,
        )
    with open(f"{tempdir}/out.pdf", "rb") as f:
        yield f.read()
    shutil.rmtree(tempdir)
