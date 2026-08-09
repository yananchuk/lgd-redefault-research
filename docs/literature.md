# Literature review

## Regulatory foundation

The core problem this project addresses sits inside the Basel capital framework's treatment of Loss Given Default. Regulation (EU) No 575/2013, the Capital Requirements Regulation, sets the high-level requirement that IRB institutions estimate LGD from a representative historical reference dataset ([CRR, EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0575)). The operational detail that matters here comes from two EBA guidelines. EBA/GL/2017/16 sets out how PD and LGD should actually be estimated, including the treatment of defaulted and cured exposures ([EBA](https://www.eba.europa.eu/regulation-and-policy/model-validation/guidelines-on-pd-lgd-estimation-and-treatment-of-defaulted-assets)). EBA/GL/2016/07 defines the probation period after which a cured exposure that falls back into default must be counted as a new, independent observation rather than a continuation of the first default ([EBA](https://www.eba.europa.eu/regulation-and-policy/credit-risk/guidelines-on-the-application-of-the-definition-of-default)); this is the rule that inflates the observed cure rate and motivates the whole re-default correction this project studies.

The assumption that a cured exposure carries zero further loss, which the basic and LGC formulas below both lean on, is not settled practice even among regulators. The UK's Prudential Regulation Authority, implementing the same EBA guidelines domestically, concluded that assumption is insufficiently conservative and required discounting the artificial cash flow recorded at cure back to the default date instead ([PRA CP21/19, Bank of England, 2019](https://www.bankofengland.co.uk/prudential-regulation/publication/2019/credit-risk-probability-of-default-and-loss-given-default-estimation)).

IFRS 9 provisioning shares the same default definition when institutions harmonize it with CRR, so the same re-default treatment carries over into expected credit loss modeling. The BCBS's guidance on accounting for expected credit losses is the standard bridge document between the Basel capital framework and IFRS 9 ([BCBS](https://www.bis.org/bcbs/publ/d350.htm)).

## Cure probability and mixture cure models

The formulas compared in this project treat cure probability ($PC$) as a single portfolio-level constant. That's a real simplification: Lohmann and Ohliger model cure probability directly as a function of loan and borrower-level covariates, first using accounting and loan-related information ([European Financial Management, 2021](https://doi.org/10.1111/eufm.12279)) and later extending it with nonlinear relationships between loan variables and the cure probability ([2024](https://doi.org/10.1016/j.ribaf.2024.102395)). Wolter and Rösch's earlier paper on cure events in default prediction is the origin point of this line of work ([European Journal of Operational Research, 2014](https://doi.org/10.1016/j.ejor.2014.04.046)).

More broadly, the "cured vs. still-at-risk" population split that the re-default correction is built around from first principles already has a formal statistical home: mixture cure models, a survival-analysis framework designed for exactly this kind of split, applied to credit risk PD estimation ([Computational Statistics & Data Analysis, 2023](https://doi.org/10.1016/j.csda.2023.107853)). This project's four formulas are closed-form, portfolio-level approximations to what a mixture cure model would estimate directly; positioning the derivation against that framework is more honest than presenting it as built from nothing.

## IFRS 9 harmonization

Two threads are relevant beyond the CRR/EBA guidelines above: how significant increase in credit risk (SICR) events get defined and compared for staging purposes under IFRS 9 ([arXiv:2303.03080, 2023](https://arxiv.org/abs/2303.03080)), and survival-analysis approaches to modeling the term structure of default risk under IFRS 9, which share methodological ground with the cure/re-default timing questions here ([arXiv:2507.15441, 2025](https://arxiv.org/abs/2507.15441)).

## Broader LGD estimation literature

The wider LGD modeling literature is large; a few papers are worth flagging for methodological relevance rather than direct citation in the derivation. Yashkir and Yashkir survey and compare LGD modeling approaches empirically, useful context for how the four formulas compared here relate to practice ([Journal of Risk Model Validation, 2013, free preprint](https://mpra.ub.uni-muenchen.de/46147/)). Bellotti and Crook incorporate macroeconomic variables into LGD models for credit cards, and Qi and Yang do the same for high loan-to-value residential mortgages, both natural extensions flagged as outside the scope of this study alongside the covariate-driven cure-probability work above ([Bellotti & Crook, International Journal of Forecasting, 2012](https://doi.org/10.1016/j.ijforecast.2010.08.005); [Qi & Yang, Journal of Banking & Finance, 2009](https://doi.org/10.1016/j.jbankfin.2008.09.015)). Two-stage modeling approaches, which separate the cure/full-recovery decision from the loss-severity estimate conditional on loss occurring, appear repeatedly in this literature and are conceptually adjacent to the cure/re-default split studied here ([Leow & Mues, 2012](https://doi.org/10.1016/j.ijforecast.2011.01.010); [Tanoue & Yamashita, 2019](https://www.risk.net/journal-of-risk/6569711/loss-given-default-estimation-a-two-stage-model-with-classification-tree-based-boosting-and-support-vector-logistic-regression)). Two more recent papers extend the same broader literature: a multi-view ensemble method for LGD forecasting ([Cheng et al., International Journal of Forecasting, 2025](https://doi.org/10.1016/j.ijforecast.2024.05.006)) and a large-sample study of how business-cycle variables move realized consumer-credit losses ([Distaso, Roccazzella & Vrins, European Journal of Operational Research, 2025](https://doi.org/10.1016/j.ejor.2024.12.026)).

## Bibliography

Bank of England, Prudential Regulation Authority. 2019. *Consultation Paper CP21/19: Credit Risk: Probability of Default and Loss Given Default Estimation*. [link](https://www.bankofengland.co.uk/prudential-regulation/publication/2019/credit-risk-probability-of-default-and-loss-given-default-estimation). Accessed August 7, 2026.

Basel Committee on Banking Supervision. 2015. *Guidance on Credit Risk and Accounting for Expected Credit Losses*. Bank for International Settlements. [link](https://www.bis.org/bcbs/publ/d350.htm). Accessed August 7, 2026.

Bellotti, Tony, and Jonathan Crook. 2012. "Loss Given Default Models Incorporating Macroeconomic Variables for Credit Cards." *International Journal of Forecasting* 28 (1): 171–82. [link](https://doi.org/10.1016/j.ijforecast.2010.08.005). Accessed August 7, 2026.

Botha, Arno, Esmerelda Oberholzer, Janette Larney, and Riaan de Jongh. 2023. "Defining and Comparing SICR-Events for Classifying Impaired Loans under IFRS 9." arXiv:2303.03080. [link](https://arxiv.org/abs/2303.03080). Accessed August 7, 2026.

Botha, Arno, and Tanja Verster. 2025. "Approaches for Modelling the Term-Structure of Default Risk under IFRS 9: A Tutorial Using Discrete-Time Survival Analysis." arXiv:2507.15441. [link](https://arxiv.org/abs/2507.15441). Accessed August 7, 2026.

Cheng, Hui, Cuiqing Jiang, Zhao Wang, and Xiaoya Ni. 2025. "Multi-View Locally Weighted Regression for Loss Given Default Forecasting." *International Journal of Forecasting* 41 (1): 290–306. [link](https://doi.org/10.1016/j.ijforecast.2024.05.006). Accessed August 7, 2026.

Distaso, Walter, Francesco Roccazzella, and Frédéric Vrins. 2025. "Business Cycle and Realized Losses in the Consumer Credit Industry." *European Journal of Operational Research* 323 (3): 1024–39. [link](https://doi.org/10.1016/j.ejor.2024.12.026). Accessed August 7, 2026.

European Banking Authority. 2016. *Guidelines on the Application of the Definition of Default* (EBA/GL/2016/07). [link](https://www.eba.europa.eu/regulation-and-policy/credit-risk/guidelines-on-the-application-of-the-definition-of-default). Accessed August 7, 2026.

European Banking Authority. 2017. *Guidelines on PD Estimation, LGD Estimation and the Treatment of Defaulted Exposures* (EBA/GL/2017/16). [link](https://www.eba.europa.eu/regulation-and-policy/model-validation/guidelines-on-pd-lgd-estimation-and-treatment-of-defaulted-assets). Accessed August 7, 2026.

European Parliament and Council of the European Union. 2013. *Regulation (EU) No 575/2013 on Prudential Requirements for Credit Institutions and Investment Firms* (Capital Requirements Regulation). [link](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013R0575). Accessed August 7, 2026.

Leow, Mindy, and Christophe Mues. 2012. "Predicting Loss Given Default (LGD) for Residential Mortgage Loans: A Two-Stage Model and Empirical Evidence for UK Bank Data." *International Journal of Forecasting* 28 (1): 183–95. [link](https://doi.org/10.1016/j.ijforecast.2011.01.010). Accessed August 7, 2026.

Lohmann, Christian, and Tobias Ohliger. 2021. "Using Accounting-Based and Loan-Related Information to Estimate the Cure Probability of a Defaulted Company." *European Financial Management* 27 (4): 620–40. [link](https://doi.org/10.1111/eufm.12279). Accessed August 7, 2026.

Lohmann, Christian, and Tobias Ohliger. 2024. "Predicting the Cure of a Defaulted Company: Nonlinear Relationships between Loan-Related Variables and the Cure Probability." *Research in International Business and Finance* 70: 102395. [link](https://doi.org/10.1016/j.ribaf.2024.102395). Accessed August 7, 2026.

Peláez, Rebeca, Ingrid Van Keilegom, Ricardo Cao, and Juan M. Vilar. 2023. "Probability of Default Estimation in Credit Risk Using Mixture Cure Models." *Computational Statistics & Data Analysis* 189: 107853. [link](https://doi.org/10.1016/j.csda.2023.107853). Accessed August 7, 2026.

Qi, Min, and Xiaolong Yang. 2009. "Loss Given Default of High Loan-to-Value Residential Mortgages." *Journal of Banking & Finance* 33 (5): 788–99. [link](https://doi.org/10.1016/j.jbankfin.2008.09.015). Accessed August 7, 2026.

Tanoue, Yuta, and Satoshi Yamashita. 2019. "Loss Given Default Estimation: A Two-Stage Model with Classification Tree-Based Boosting and Support Vector Logistic Regression." *Journal of Risk* 21 (4): 19–37. [link](https://www.risk.net/journal-of-risk/6569711/loss-given-default-estimation-a-two-stage-model-with-classification-tree-based-boosting-and-support-vector-logistic-regression). Accessed August 7, 2026.

Wolter, Marcus, and Daniel Rösch. 2014. "Cure Events in Default Prediction." *European Journal of Operational Research* 238: 846–57. [link](https://doi.org/10.1016/j.ejor.2014.04.046). Accessed August 7, 2026.

Yashkir, Olga, and Yuriy Yashkir. 2013. "Loss Given Default Modeling: A Comparative Analysis." *Journal of Risk Model Validation* 7: 25–59. Free preprint: [link](https://mpra.ub.uni-muenchen.de/46147/). Accessed August 7, 2026.
