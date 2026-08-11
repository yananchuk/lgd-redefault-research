# Literature review

## Regulatory foundation

The core problem this project addresses sits inside the Basel capital framework's treatment of Loss Given Default. Regulation (EU) No 575/2013, the Capital Requirements Regulation, sets the high-level requirement that IRB institutions estimate LGD from a representative historical reference dataset ([CRR, EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0575)). The operational detail that matters here comes from two EBA guidelines and one RTS, each doing a different job. EBA/GL/2016/07 defines the probation period, a minimum of three months (twelve for restructuring-related defaults), before a defaulted exposure can even exit default status and be reclassified as cured ([EBA](https://www.eba.europa.eu/regulation-and-policy/credit-risk/guidelines-on-the-application-of-the-definition-of-default)). EBA/GL/2017/16 sets out how PD and LGD should actually be estimated, including, per its §101 (itself implementing Article 52(b) of the RTS on IRB assessment methodology), a separate independence threshold: a re-default occurring within nine months of that return to non-defaulted status must be treated as a continuation of the original default for LGD estimation, not logged as a second independent observation ([EBA](https://www.eba.europa.eu/regulation-and-policy/model-validation/guidelines-on-pd-lgd-estimation-and-treatment-of-defaulted-assets); [EBA/RTS/2016/03](https://www.eba.europa.eu/sites/default/files/documents/10180/1525916/e8373cbc-cc4b-4dd9-83b5-93c9657a39f0/Final%20Draft%20RTS%20on%20Assessment%20Methodology%20for%20IRB.pdf)). The guideline is explicit that this nine-month period sits in addition to the probation period, not in place of it. It's this pairing, not either rule alone, that inflates the observed cure rate and motivates the whole re-default correction this project studies: a formula correcting for genuinely independent re-defaults, and a data-construction rule for telling those apart from exposures that were never really cured.

The assumption that a cured exposure carries zero further loss, which the [basic](derivation.md#basic-two-factor-model) and [loss-given-cure](derivation.md#loss-given-cure-add-on) formulas both lean on, is not settled practice even among regulators. The UK's Prudential Regulation Authority, implementing the same EBA guidelines domestically, concluded that assumption is insufficiently conservative and required discounting the artificial cash flow recorded at cure back to the default date instead ([PRA CP21/19, Bank of England, 2019](https://www.bankofengland.co.uk/prudential-regulation/publication/2019/credit-risk-probability-of-default-and-loss-given-default-estimation)).

IFRS 9 provisioning shares the same default definition when institutions harmonize it with CRR, so the same re-default treatment carries over into expected credit loss modeling. The BCBS's guidance on accounting for expected credit losses is the standard bridge document between the Basel capital framework and IFRS 9 ([BCBS](https://www.bis.org/bcbs/publ/d350.htm)).

## Cure probability and mixture cure models

The formulas compared in this project treat cure probability ($PC$) as a single portfolio-level constant. That's a real simplification: Lohmann and Ohliger model cure probability directly as a function of loan and borrower-level covariates, first using accounting and loan-related information ([European Financial Management, 2021](https://doi.org/10.1111/eufm.12279)) and later extending it with nonlinear relationships between loan variables and the cure probability ([2024](https://doi.org/10.1016/j.ribaf.2024.102395)). Wolter and Rösch's earlier paper on cure events in default prediction is the origin point of this line of work ([European Journal of Operational Research, 2014](https://doi.org/10.1016/j.ejor.2014.04.046)).

More broadly, the "cured vs. still-at-risk" population split that the re-default correction is built around from first principles already has a formal statistical home: mixture cure models, a survival-analysis framework designed for exactly this kind of split, applied to credit risk PD estimation ([Computational Statistics & Data Analysis, 2023](https://doi.org/10.1016/j.csda.2023.107853)). This project's five formulas are closed-form, portfolio-level approximations to what a mixture cure model would estimate directly; positioning the derivation against that framework is more honest than presenting it as built from nothing.

## IFRS 9 harmonization

Two threads are relevant beyond the CRR/EBA guidelines above: how significant increase in credit risk (SICR) events get defined and compared for staging purposes under IFRS 9 ([arXiv:2303.03080, 2023](https://arxiv.org/abs/2303.03080)), and survival-analysis approaches to modeling the term structure of default risk under IFRS 9, which share methodological ground with the cure/re-default timing questions here ([arXiv:2507.15441, 2025](https://arxiv.org/abs/2507.15441)).

## Broader LGD estimation literature

The wider LGD modeling literature is large; a few papers are worth flagging for methodological relevance rather than direct citation in the derivation. Yashkir and Yashkir survey and compare LGD modeling approaches empirically, useful context for how the four formulas compared here relate to practice ([Journal of Risk Model Validation, 2013, free preprint](https://mpra.ub.uni-muenchen.de/46147/)). Bellotti and Crook incorporate macroeconomic variables into LGD models for credit cards, and Qi and Yang do the same for high loan-to-value residential mortgages, both natural extensions flagged as outside the scope of this study alongside the covariate-driven cure-probability work above ([Bellotti & Crook, International Journal of Forecasting, 2012](https://doi.org/10.1016/j.ijforecast.2010.08.005); [Qi & Yang, Journal of Banking & Finance, 2009](https://doi.org/10.1016/j.jbankfin.2008.09.015)). Two-stage modeling approaches, which separate the cure/full-recovery decision from the loss-severity estimate conditional on loss occurring, appear repeatedly in this literature and are conceptually adjacent to the cure/re-default split studied here ([Leow & Mues, 2012](https://doi.org/10.1016/j.ijforecast.2011.01.010); [Tanoue & Yamashita, 2019](https://www.risk.net/journal-of-risk/6569711/loss-given-default-estimation-a-two-stage-model-with-classification-tree-based-boosting-and-support-vector-logistic-regression)). Two more recent papers extend the same broader literature: a multi-view ensemble method for LGD forecasting ([Cheng et al., International Journal of Forecasting, 2025](https://doi.org/10.1016/j.ijforecast.2024.05.006)) and a large-sample study of how business-cycle variables move realized consumer-credit losses ([Distaso, Roccazzella & Vrins, European Journal of Operational Research, 2025](https://doi.org/10.1016/j.ejor.2024.12.026)).

## Bibliography

Bank of England, Prudential Regulation Authority. (2019). *Consultation paper CP21/19: Credit risk: Probability of default and loss given default estimation*. Retrieved August 7, 2026, from https://www.bankofengland.co.uk/prudential-regulation/publication/2019/credit-risk-probability-of-default-and-loss-given-default-estimation

Basel Committee on Banking Supervision. (2015). *Guidance on credit risk and accounting for expected credit losses*. Bank for International Settlements. Retrieved August 7, 2026, from https://www.bis.org/bcbs/publ/d350.htm

Bellotti, T., and Crook, J. (2012). Loss given default models incorporating macroeconomic variables for credit cards. *International Journal of Forecasting*, 28(1), 171-182. https://doi.org/10.1016/j.ijforecast.2010.08.005

Botha, A., Oberholzer, E., Larney, J., and de Jongh, R. (2023). Defining and comparing SICR-events for classifying impaired loans under IFRS 9. *arXiv*. https://arxiv.org/abs/2303.03080

Botha, A., and Verster, T. (2025). Approaches for modelling the term-structure of default risk under IFRS 9: A tutorial using discrete-time survival analysis. *arXiv*. https://arxiv.org/abs/2507.15441

Cheng, H., Jiang, C., Wang, Z., and Ni, X. (2025). Multi-view locally weighted regression for loss given default forecasting. *International Journal of Forecasting*, 41(1), 290-306. https://doi.org/10.1016/j.ijforecast.2024.05.006

Distaso, W., Roccazzella, F., and Vrins, F. (2025). Business cycle and realized losses in the consumer credit industry. *European Journal of Operational Research*, 323(3), 1024-1039. https://doi.org/10.1016/j.ejor.2024.12.026

European Banking Authority. (2016a). *Final draft regulatory technical standards on the specification of the assessment methodology for competent authorities regarding compliance of an institution with the requirements to use the IRB approach* (EBA/RTS/2016/03). Retrieved August 10, 2026, from https://www.eba.europa.eu/sites/default/files/documents/10180/1525916/e8373cbc-cc4b-4dd9-83b5-93c9657a39f0/Final%20Draft%20RTS%20on%20Assessment%20Methodology%20for%20IRB.pdf

European Banking Authority. (2016b). *Guidelines on the application of the definition of default* (EBA/GL/2016/07). Retrieved August 7, 2026, from https://www.eba.europa.eu/regulation-and-policy/credit-risk/guidelines-on-the-application-of-the-definition-of-default

European Banking Authority. (2017). *Guidelines on PD estimation, LGD estimation and the treatment of defaulted exposures* (EBA/GL/2017/16). Retrieved August 7, 2026, from https://www.eba.europa.eu/regulation-and-policy/model-validation/guidelines-on-pd-lgd-estimation-and-treatment-of-defaulted-assets

European Parliament and Council of the European Union. (2013). *Regulation (EU) No 575/2013 on prudential requirements for credit institutions and investment firms* (Capital Requirements Regulation). Retrieved August 7, 2026, from https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0575

Leow, M., and Mues, C. (2012). Predicting loss given default (LGD) for residential mortgage loans: A two-stage model and empirical evidence for UK bank data. *International Journal of Forecasting*, 28(1), 183-195. https://doi.org/10.1016/j.ijforecast.2011.01.010

Lohmann, C., and Ohliger, T. (2021). Using accounting-based and loan-related information to estimate the cure probability of a defaulted company. *European Financial Management*, 27(4), 620-640. https://doi.org/10.1111/eufm.12279

Lohmann, C., and Ohliger, T. (2024). Predicting the cure of a defaulted company: Nonlinear relationships between loan-related variables and the cure probability. *Research in International Business and Finance*, 70, 102395. https://doi.org/10.1016/j.ribaf.2024.102395

Peláez, R., Van Keilegom, I., Cao, R., and Vilar, J. M. (2023). Probability of default estimation in credit risk using mixture cure models. *Computational Statistics & Data Analysis*, 189, 107853. https://doi.org/10.1016/j.csda.2023.107853

Qi, M., and Yang, X. (2009). Loss given default of high loan-to-value residential mortgages. *Journal of Banking & Finance*, 33(5), 788-799. https://doi.org/10.1016/j.jbankfin.2008.09.015

Tanoue, Y., and Yamashita, S. (2019). Loss given default estimation: A two-stage model with classification tree-based boosting and support vector logistic regression. *Journal of Risk*, 21(4), 19-37. https://www.risk.net/journal-of-risk/6569711/loss-given-default-estimation-a-two-stage-model-with-classification-tree-based-boosting-and-support-vector-logistic-regression

Wolter, M., and Rösch, D. (2014). Cure events in default prediction. *European Journal of Operational Research*, 238, 846-857. https://doi.org/10.1016/j.ejor.2014.04.046

Yashkir, O., and Yashkir, Y. (2013). Loss given default modeling: A comparative analysis. *Journal of Risk Model Validation*, 7, 25-59. Free preprint retrieved August 7, 2026, from https://mpra.ub.uni-muenchen.de/46147/
