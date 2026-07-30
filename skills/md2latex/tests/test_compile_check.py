import importlib.util
import os
import pathlib
import tempfile
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "latex_compile_check.py"
SPEC = importlib.util.spec_from_file_location("latex_compile_check_script", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def write_tex(directory, name, content):
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# Helper to build LaTeX strings without Python escape issues
def tex(*lines):
    return "\n".join(lines) + "\n"


class XeCJKConflictTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_xecjk_with_pdflatex_detected(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{xeCJK}",
            r"\begin{document}",
            "Hello",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path, preferred_compiler="pdflatex")
        types = [i["type"] for i in report["errors"]]
        self.assertIn("xecjk_pdflatex_conflict", types)

    def test_xecjk_with_xelatex_no_conflict(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{xeCJK}",
            r"\begin{document}",
            "Hello",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path, preferred_compiler="xelatex")
        types = [i["type"] for i in report["errors"]]
        self.assertNotIn("xecjk_pdflatex_conflict", types)


class CJKWithoutSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_chinese_without_xecjk_detected(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\begin{document}",
            "中文内容",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        types = [i["type"] for i in report["errors"]]
        self.assertIn("cjk_without_support", types)

    def test_chinese_with_xecjk_no_error(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{xeCJK}",
            r"\begin{document}",
            "中文内容",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path, preferred_compiler="xelatex")
        types = [i["type"] for i in report["errors"]]
        self.assertNotIn("cjk_without_support", types)

    def test_ctexart_no_cjk_error(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{ctexart}",
            r"\begin{document}",
            "中文内容",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        types = [i["type"] for i in report["errors"]]
        self.assertNotIn("cjk_without_support", types)


class MissingGraphicxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_includegraphics_without_graphicx_detected(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\begin{document}",
            r"\includegraphics{test.png}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        types = [i["type"] for i in report["errors"]]
        self.assertIn("missing_graphicx", types)

    def test_includegraphics_with_graphicx_no_error(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{test.png}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        types = [i["type"] for i in report["errors"]]
        self.assertNotIn("missing_graphicx", types)


class SVGFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "figures", "svg"))
        os.makedirs(os.path.join(self.tmp, "figures", "pdf"))
        with open(os.path.join(self.tmp, "figures", "svg", "d.svg"), "w") as f:
            f.write("<svg/>")
        with open(os.path.join(self.tmp, "figures", "pdf", "d.pdf"), "w") as f:
            f.write("%PDF")

    def test_svg_with_fallback_warns(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{figures/svg/d.svg}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        types = [i["type"] for i in report["warnings"]]
        self.assertIn("svg_with_fallback", types)

    def test_svg_without_fallback_errors(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{figures/svg/other.svg}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        all_types = [i["type"] for i in report["warnings"]] + [i["type"] for i in report["errors"]]
        self.assertIn("svg_no_fallback", all_types)


class MissingImageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_missing_image_detected(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{nonexistent.png}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        all_types = [i["type"] for i in report["warnings"]] + [i["type"] for i in report["errors"]]
        self.assertIn("missing_image", all_types)

    def test_existing_image_no_warning(self):
        with open(os.path.join(self.tmp, "exists.png"), "w") as f:
            f.write("fake")
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{exists.png}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        all_types = [i["type"] for i in report["warnings"]] + [i["type"] for i in report["errors"]]
        self.assertNotIn("missing_image", all_types)


class AutoFixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "figures", "svg"))
        os.makedirs(os.path.join(self.tmp, "figures", "pdf"))
        with open(os.path.join(self.tmp, "figures", "svg", "d.svg"), "w") as f:
            f.write("<svg/>")
        with open(os.path.join(self.tmp, "figures", "pdf", "d.pdf"), "w") as f:
            f.write("%PDF")

    def test_fix_adds_graphicx(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\begin{document}",
            r"\includegraphics{test.png}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        fixes = CHECK.auto_fix(path, report, force=True)
        self.assertTrue(any("graphicx" in f for f in fixes))
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn(r"\usepackage{graphicx}", content)
        self.assertIn(r"\includegraphics{test.png}", content)

    def test_fix_replaces_svg_with_pdf(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{graphicx}",
            r"\begin{document}",
            r"\includegraphics{figures/svg/d.svg}",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        fixes = CHECK.auto_fix(path, report, force=True)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("figures/pdf/d.pdf", content)
        self.assertNotIn("figures/svg/d.svg", content)


class CompilerDetectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_article_template_recommends_pdflatex(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\begin{document}",
            "Hello",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        self.assertEqual(report["compiler_recommended"], "pdflatex")

    def test_xecjk_recommends_xelatex(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{article}",
            r"\usepackage{xeCJK}",
            r"\begin{document}",
            "Hello",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        self.assertEqual(report["compiler_recommended"], "xelatex")

    def test_ctexart_recommends_xelatex(self):
        path = write_tex(self.tmp, "p.tex", tex(
            r"\documentclass{ctexart}",
            r"\begin{document}",
            "Hello",
            r"\end{document}",
        ))
        report = CHECK.run_checks(path)
        self.assertEqual(report["compiler_recommended"], "xelatex")


if __name__ == "__main__":
    unittest.main()
