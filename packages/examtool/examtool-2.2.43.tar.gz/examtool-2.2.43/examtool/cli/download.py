import csv
import os
import pathlib
from multiprocessing.pool import ThreadPool

import click
import threading
from tqdm import tqdm

from examtool.api.render_html_export import render_html_exam
from examtool.api.render_pdf_export import render_pdf_exam
from examtool.api.gen_latex import render_latex
from examtool.cli.utils import (
    exam_name_option,
    hidden_output_folder_option,
    OnceSameNameOption,
)
import examtool.api.download
import examtool.api.assemble_export


@click.command()
@exam_name_option
@click.option(
    "--name-question",
    default=None,
    help="The ID of the question for the student's name.",
)
@click.option(
    "--sid-question", default=None, help="The ID of the question for the student's SID."
)
@click.option(
    "--with-substitutions/--without-substitutions",
    default=False,
    help="Include keyword substitutions in exported question bodies.",
)
@click.option(
    "--via-html",
    "mode",
    flag_value="html",
    default=True,
    help="Use an HTML-based PDF exporter",
    cls=OnceSameNameOption,
)
@click.option(
    "--via-latex",
    "mode",
    flag_value="latex",
    help="Embed student responses in the LaTeX PDF",
    cls=OnceSameNameOption,
)
@click.option(
    "--latex-prefix",
    default=None,
    help="Path to custom LaTeX prefix (for --via-latex)",
    type=click.Path(),
)
@click.option(
    "--latex-suffix",
    default=None,
    help="Path to custom LaTeX suffix (for --via-latex)",
    type=click.Path(),
)
@click.option(
    "--direct-pdf",
    "mode",
    flag_value="pdf",
    help="Export directly to PDF",
    cls=OnceSameNameOption,
)
@click.option(
    "--num-threads",
    default=16,
    type=int,
    help="The number of threads to process the JSON file.",
)
@hidden_output_folder_option
def download(
    exam,
    out,
    name_question,
    sid_question,
    with_substitutions,
    mode,
    num_threads,
    latex_prefix,
    latex_suffix,
):
    """
    Download student submissions for an exam.
    Exams are downloaded as PDFs into a target folder - specify `out` to redirect the folder.
    An `OUTLINE.pdf` is also generated for Gradescope, as is a `summary.csv` for analytics or autograding.
    """
    if (latex_prefix or latex_suffix) and mode != "latex":
        assert False, "--latex-prefix/suffix can only be used with --via-latex"

    out = out or "out/export/" + exam
    pathlib.Path(out).mkdir(parents=True, exist_ok=True)

    (
        exam_json,
        template_questions,
        email_to_data_map,
        total,
    ) = examtool.api.download.download(exam)

    with open(os.path.join(out, "summary.csv"), "w") as f:
        writer = csv.writer(f)
        for row in total:
            writer.writerow(row)

    assembled_exams = examtool.api.assemble_export.export(
        template_questions,
        email_to_data_map,
        exam,
        name_question,
        sid_question,
        substitute_in_question_text=with_substitutions,
    )

    def render(name_exam):
        name, exam = name_exam

        target = os.path.join(out, f"{name}.pdf")

        if mode == "html":
            export = render_html_exam(exam)
            export(target)
        elif mode == "pdf":
            pdf = render_pdf_exam(exam)
            pdf.output(target)
        else:
            with render_latex(
                exam_json,
                {},
                prefix=latex_prefix,
                suffix=latex_suffix,
                response=exam,
                # tempdir=f"temp/{threading.get_ident()}",
            ) as pdf:
                with open(target, "wb") as f:
                    f.write(pdf)

    with ThreadPool(num_threads) as p:
        list(
            tqdm(
                p.imap_unordered(render, assembled_exams.items()),
                total=len(assembled_exams),
                desc="Rendering",
                unit="Exam",
            )
        )


if __name__ == "__main__":
    download()
