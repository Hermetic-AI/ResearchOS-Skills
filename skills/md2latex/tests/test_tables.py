import importlib.util
import pathlib
import tempfile
import types
import unittest
import os


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "md2latex.py"
SPEC = importlib.util.spec_from_file_location("md2latex_script", SCRIPT)
MD2LATEX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MD2LATEX)


def args(template, figure_ext=None):
    return types.SimpleNamespace(
        template=template,
        table_pos="H",
        figure_ext=figure_ext,
        figure_pos="H",
        math_env="equation",
        cross_ref=False,
        long_table=False,
        unicode_domain=None,
    )


class TableLayoutTests(unittest.TestCase):
    def test_wide_ieee_table_spans_columns_and_wraps(self):
        rows = [
            ["", "Write", "Read", "Manage", "Evaluate"],
            ["---", "---", "---", "---", "---"],
            ["Working", "context assembly", "prompt formatting",
             "sliding window", "length-budget, attention-position"],
        ]

        converter = MD2LATEX.Converter(args("IEEEtran"))
        latex = "\n".join(converter.table(rows))

        self.assertIn(r"\begin{table*}[t]", latex)
        self.assertIn(r"\begin{tabularx}{\textwidth}", latex)
        self.assertIn(r"\end{table*}", latex)
        self.assertIn("tabularx", converter.feat)

    def test_article_table_stays_single_column_but_wraps(self):
        rows = [
            ["Name", "Description"],
            ["---", "---"],
            ["A", "A description that should wrap instead of overflowing"],
        ]

        converter = MD2LATEX.Converter(args("article"))
        latex = "\n".join(converter.table(rows))

        self.assertIn(r"\begin{table}[H]", latex)
        self.assertIn(r"\begin{tabularx}{\linewidth}", latex)
        self.assertNotIn(r"\begin{table*}", latex)


class FigureFallbackTests(unittest.TestCase):
    """Verify SVG -> PDF/PNG fallback across parallel directories."""

    def setUp(self):
        # Mirror the real project layout: md lives in a ``paper/`` subdir,
        # figures live sibling to it (../figures/svg/ & ../figures/pdf/).
        self.tmp = tempfile.mkdtemp()
        paper_dir = os.path.join(self.tmp, "paper")
        svg_dir = os.path.join(self.tmp, "figures", "svg")
        pdf_dir = os.path.join(self.tmp, "figures", "pdf")
        os.makedirs(paper_dir)
        os.makedirs(svg_dir)
        os.makedirs(pdf_dir)
        # SVG file (content irrelevant — only existence matters)
        with open(os.path.join(svg_dir, "fig1.svg"), "w") as f:
            f.write("<svg/>")
        # PDF fallback in the parallel directory
        with open(os.path.join(pdf_dir, "fig1.pdf"), "w") as f:
            f.write("%PDF-1.4 fake")
        # Markdown references the SVG with a ../ relative path
        self.md_path = os.path.join(paper_dir, "paper.md")
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write("# Test\n\n![fig](../figures/svg/fig1.svg)\n")

    def test_parallel_dir_fallback_without_figure_ext(self):
        """Without --figure-ext, SVG in svg/ falls back to pdf/ in parallel dir."""
        pa = args("IEEEtran")
        pa.md = self.md_path
        converter = MD2LATEX.Converter(pa)
        result = converter.image_path("../figures/svg/fig1.svg")
        self.assertEqual(result, "../figures/pdf/fig1.pdf")

    def test_parallel_dir_fallback_with_figure_ext_pdf(self):
        """With --figure-ext pdf, SVG in svg/ resolves to pdf/ in parallel dir."""
        pa = args("IEEEtran", figure_ext="pdf")
        pa.md = self.md_path
        converter = MD2LATEX.Converter(pa)
        result = converter.image_path("../figures/svg/fig1.svg")
        self.assertEqual(result, "../figures/pdf/fig1.pdf")

    def test_non_svg_path_returned_unchanged(self):
        pa = args("IEEEtran")
        pa.md = self.md_path
        converter = MD2LATEX.Converter(pa)
        self.assertEqual(converter.image_path("photo.png"), "photo.png")


if __name__ == "__main__":
    unittest.main()
