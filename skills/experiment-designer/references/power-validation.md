# Power-calculation reference validation

The core `power_analysis.py` CLI intentionally uses Python's standard library and a documented normal approximation. Release validation compares that approximation with SciPy and Statsmodels on a fixed public grid.

```bash
python -m pip install -e ".[validation]"
python experiment-designer/scripts/validate_power_calculations.py --out power-validation.json
```

## Reference grid

The validator covers:

- independent, one-sample, and paired standardized mean tests;
- two-independent-proportion calculations expressed as Cohen's h;
- effect sizes 0.2, 0.5, and 0.8;
- alpha 0.01 and 0.05;
- target power 0.80 and 0.90;
- one- and two-sided normal critical values against SciPy.

It records every local/reference value, library versions, and maxima. Current acceptance limits are:

- absolute required-sample difference at most 4;
- absolute achieved-power difference at most 0.04;
- absolute critical-z difference at most `1e-12`.

These tolerances are not claims of exact equivalence. Statsmodels uses noncentral t calculations for t tests, whereas ResearchOS uses the normal approximation. The most visible grid difference is expected for one-sample/paired tests with stringent alpha. Users requiring final design values should use a method aligned with the intended test and distribution.

## Coverage boundary

The reference grid does not certify noninferiority/equivalence margins, cluster designs, longitudinal models, or survival designs. Those features depend on additional assumptions and require design-specific software or simulation. Contributions that expand a formula must add an independent reference comparison and state an evidence-based tolerance.

Reference APIs:

- Statsmodels `TTestIndPower.solve_power`: https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestIndPower.solve_power.html
- Statsmodels project/license: https://www.statsmodels.org/stable/
- SciPy normal distribution: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
