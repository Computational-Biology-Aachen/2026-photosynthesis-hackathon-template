# Ghana Hackathon — Dataset Catalog

All datasets are live in **`open_jii_data_hackathon.default`** on Databricks.

---

## Key Terminology

| Term            | Meaning                                                                              |
| --------------- | ------------------------------------------------------------------------------------ |
| **Phi2**        | Quantum yield of PSII — fraction of absorbed light used for photochemistry           |
| **LEF**         | Linear Electron Flow — rate of electron transport through PSII (umol electrons/m2/s) |
| **NPQt**        | Non-Photochemical Quenching — photoprotective energy dissipation as heat             |
| **PhiNPQ**      | Fraction of absorbed light going to NPQ                                              |
| **PhiNO**       | Fraction of absorbed light lost via non-regulated pathways (photodamage risk)        |
| **qL**          | Fraction of open PSII centers (oxidized QA)                                          |
| **SPAD**        | Relative chlorophyll content index                                                   |
| **ECS**         | Electrochromic Shift — measure of thylakoid proton motive force                      |
| **gH+**         | Proton conductance of ATP synthase                                                   |
| **vH+**         | Proton flux through thylakoid membrane                                               |
| **PSI centers** | Photosystem I redox states (active, open, over-reduced, oxidized)                    |
| **P700**        | PSI reaction center chlorophyll — P700_DIRK measures its dark relaxation kinetics    |
| **PIRK**        | Post-Illumination Rise in fluorescence Kinetics — indicator of cyclic electron flow  |
| **PAR**         | Photosynthetically Active Radiation (400-700 nm, umol photons/m2/s)                  |
| **VARIANT**     | Databricks column type storing the full raw JSON measurement trace                   |
| **sample_raw**  | The complete raw measurement data from the MultispeQ device, stored as VARIANT       |


---

## 1. Potato Grebbedijk — `grebbedijk_measurements`

|                        |                                  |
| ---------------------- | -------------------------------- |
| **Crop**               | Potato                           |
| **Location**           | Wageningen, Netherlands          |
| **Year**               | 2025                             |
| **Measurements**       | 3,681                            |
| **Genotypes**          | 48 plots                         |
| **Owner**              | Olivia Kacheyo                   |
| **Protocol**           | UNZA_PIRK_DIRK_LightPotential_14 |
| **PhotosynQ projects** | 33338                            |

**Experiment:** Assessment of photosynthesis dynamics in a potato field trial at Grebbedijk (Wageningen). 48 plots measured with MultispeQ, genotype assigned via plot layout key.

**Protocol features (UNZA_PIRK_DIRK):** This protocol measures photosynthesis under both ambient and high (saturating) actinic light, enabling calculation of "light potential" — the difference between current and maximum electron transport rate. It also includes PIRK (Post-Illumination Rise in fluorescence Kinetics), an indicator of cyclic electron flow around PSI.

**Computed columns (25):**

| Category       | Columns                                                                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Photosynthesis | `phi2_ambient`, `phi2_high`, `LEF_ambient`, `LEF_high`, `LEF_light_potential`                                                                    |
| Light          | `PAR`, `used_PAR_ambient`, `used_PAR_high`, `SQRT_PAR`                                                                                           |
| Chlorophyll    | `SPAD`                                                                                                                                           |
| Environment    | `ambient_Temperature`, `leaf_temperature`, `leaf_temperature_differential`, `humidity`, `pressure`, `leaf_angle`                                 |
| PIRK           | `PIRK_amp_ambient`, `PIRK_amp_high`, `pirk_intensity`                                                                                            |
| Autogain       | `autogain_ch1_duration`, `autogain_ch1_intensity`, `autogain_ch1_value`, `autogain_ch2_duration`, `autogain_ch2_intensity`, `autogain_ch2_value` |
| Timing         | `measurement_duration_sec`                                                                                                                       |

**Additional column:** `sample_raw` (VARIANT) — full raw measurement trace from the MultispeQ device, containing time-resolved fluorescence, absorbance, and environmental sensor data. Can be parsed for additional phenotypes beyond the computed columns.

---

## 2. Common Bean GART — `bean_gart_35462_35509`

|                        |                                          |
| ---------------------- | ---------------------------------------- |
| **Crop**               | Common bean (_Phaseolus vulgaris_)       |
| **Location**           | GART Chisamba, Zambia                    |
| **Year**               | 2025                                     |
| **Measurements**       | 9,716                                    |
| **Genotypes**          | 484 genotypes                            |
| **Owner**              | Kelvin Kamfwa                            |
| **Protocol**           | UNZA_PIRK_DIRK_LightPotential_14         |
| **PhotosynQ projects** | 35462, 35463, 35479, 35497, 35498, 35509 |

**Experiment:** Drought stress trial on three RIL (Recombinant Inbred Line) populations at Golden Valley Agricultural Research Trust (GART) in Zambia. Three bi-parental crosses — Lusaka × Krimson (LK), Lusaka × Inferno (LI), Mwezi Moja × Inferno (MI) — each measured under control and drought-stressed conditions.

| Project | Cross | Treatment | Measurements |
| ------- | ----- | --------- | ------------ |
| 35462   | LK    | Control   | 1,014        |
| 35479   | LK    | Stressed  | 1,836        |
| 35463   | LI    | Control   | 1,327        |
| 35497   | LI    | Stressed  | 2,433        |
| 35498   | MI    | Control   | 1,163        |
| 35509   | MI    | Stressed  | 1,943        |

**Computed columns (25):** Same UNZA_PIRK_DIRK protocol as Potato Grebbedijk — see Dataset 1.

**Additional column:** `sample_raw` (VARIANT).

---

## 3. Barley QTL Nergena — `barley_qtl_32593_32742`

|                        |                                               |
| ---------------------- | --------------------------------------------- |
| **Crop**               | Barley                                        |
| **Location**           | Nergena, Netherlands                          |
| **Year**               | 2025                                          |
| **Measurements**       | 1,680                                         |
| **Genotypes**          | 272 genotypes (Offspring, Elite line, Parent) |
| **Owner**              | Olivia Kacheyo                                |
| **Protocol**           | UNZA_PIRK_DIRK_LightPotential_14              |
| **PhotosynQ projects** | 32593, 32742                                  |

**Experiment:** QTL mapping population field trial for barley at Nergena (Wageningen campus). Genotype joined via Olivia's conversion key (plot line → genotype).

**Computed columns (25):** Same UNZA_PIRK_DIRK protocol — see Dataset 1.

**Additional column:** `sample_raw` (VARIANT).

---

## 4. Aardaker Nergena — `aardaker_nergena_29273`

|                        |                                                  |
| ---------------------- | ------------------------------------------------ |
| **Crop**               | Aardaker (_Lathyrus tuberosus_ / tuberous pea)   |
| **Location**           | Nergena greenhouse, Wageningen, Netherlands      |
| **Year**               | 2024–2025                                        |
| **Measurements**       | 3,221                                            |
| **Genotypes**          | 392 genotypes across 3 heterotic pools (A, B, I) |
| **Owner**              | Padraic Flood                                    |
| **Protocol**           | Photosynthesis RIDES 2.0                         |
| **PhotosynQ projects** | 29273                                            |

**Experiment:** Phenotyping of _Lathyrus tuberosus_ (aardaker) genotypes under greenhouse conditions at Nergena. Genotypes span three heterotic pools (A: 643 measurements, B: 281, I: 32; 2,265 unassigned). Genotype entered directly into PhotosynQ user answers during measurement.

**Protocol features (RIDES 2.0):** The RIDES (Rapid Identification of Differential Efficiency of photosynthesis from Spectra) protocol captures a comprehensive set of photosynthesis parameters including ECS (electrochromic shift) for thylakoid proton motive force, PSI redox state via P700 absorbance changes, and PSII fluorescence. It measures under ambient light conditions, preserving the in-vivo state of the photosynthetic apparatus.

**Computed columns (30):**

| Category       | Columns                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------ |
| Photosystem II | `Phi2`, `PhiNPQ`, `PhiNO`, `NPQt`, `LEF`, `qL`, `FmPrime`, `FoPrime`, `Fs`, `FvP_over_FmP`                         |
| Chlorophyll    | `SPAD`                                                                                                             |
| Light          | `Light_Intensity_PAR`                                                                                              |
| Environment    | `Leaf_Temperature`, `Ambient_Temperature`, `Leaf_Temperature_Differential`, `Ambient_Humidity`, `Ambient_Pressure` |
| ECS            | `ECSt_mAU`, `ECS_tau`, `gHplus`, `vHplus`                                                                          |
| Photosystem I  | `PS1_Active_Centers`, `PS1_Open_Centers`, `PS1_Over_Reduced_Centers`, `PS1_Oxidized_Centers`                       |
| P700           | `P700_DIRK_ampl`, `kP700`, `tP700`, `v_initial_P700`                                                               |
| Morphology     | `leaf_angle`, `leaf_thickness`                                                                                     |

**Additional column:** `sample_raw` (VARIANT).

---

## 5. Potato Ambyte/Ambit — `potato_ambyte_ambit` + `potato_ambyte_ambit_silver`

|                  |                                                                        |
| ---------------- | ---------------------------------------------------------------------- |
| **Crop**         | Potato                                                                 |
| **Location**     | Field trial (Netherlands)                                              |
| **Year**         | 2024                                                                   |
| **Measurements** | ~512 million rows (12 Hz continuous)                                   |
| **Genotypes**    | ~10 genotypes, 4 replicates                                            |
| **Owner**        | Tom Theeuwen                                                           |
| **Sensor**       | Ambyte/Ambit field-deployed chlorophyll fluorescence sensor            |
| **Tables**       | Bronze (`potato_ambyte_ambit`) + Silver (`potato_ambyte_ambit_silver`) |

**Experiment:** Continuous field monitoring of potato photosynthesis using 27 Ambyte sensor units (108 Ambit sub-devices), each logging chlorophyll fluorescence and environmental data at ~12 Hz. This is **not** MultispeQ/PhotosynQ data — it comes from dedicated field-deployed sensors that capture time-resolved fluorescence kinetics throughout the day.

**Measurement types:** `MPF2` (modulated pulse fluorescence), `SS` (steady state), `SPACER`, `FI` (fluorescence induction), `qE1` (energy-dependent quenching), `Rec1` (recovery).

**Bronze columns:**

| Category     | Columns                                                |
| ------------ | ------------------------------------------------------ |
| Identity     | `ambyte_num`, `ambit_num`, `genotype`, `block`, `plot` |
| Time         | `timestamp`, `measurement_type`                        |
| Fluorescence | `actinic`, `sig_f`, `ref_f`, `sig_7`, `ref_7`          |
| Light        | `sun`, `leaf`, `par`                                   |
| Temperature  | `temp`, `board_temp`                                   |
| Other        | `raw_value`, `count`, `pts`, `res`, `full`, `spec`     |

**Silver layer** adds: snake_case column names, UTC timestamps, DLT quality expectations (drops rows with NULL timestamp or ambyte).

---

## 6. Barley iMAGIC — `barley_imagic_17237_18685`

|                        |                                                      |
| ---------------------- | ---------------------------------------------------- |
| **Crop**               | Barley                                               |
| **Location**           | Wollo/Geregera & Gondar/Dabat, Ethiopia              |
| **Year**               | 2022–2023                                            |
| **Measurements**       | 13,178                                               |
| **Genotypes**          | 508 genotypes (74% coverage)                         |
| **Owner**              | Matteo Dell'Acqua (Scuola Superiore Sant'Anna, Pisa) |
| **Protocol**           | Photosynthesis RIDES 2.0                             |
| **PhotosynQ projects** | 17237, 17238, 18685, 19236                           |

**Experiment:** Photosynthesis phenotyping of the iMAGIC (International Multi-parent Advanced Generation Inter-Cross) barley population in Ethiopia, part of the CAPITALISE project. Measurements collected across two locations and two replications per location. The iMAGIC population is a recombinant barley population with genotype codes in BMNNN format.

| Project | Location         | Rep | Measurements |
| ------- | ---------------- | --- | ------------ |
| 17237   | Geregera (Wollo) | I   | 2,540        |
| 18685   | Geregera (Wollo) | II  | 2,529        |
| 17238   | Dabat (Gondar)   | I   | 4,094        |
| 19236   | Dabat (Gondar)   | II  | 4,015        |

**Genotype assignment:** No shared ID between PhotosynQ and the field layout. Genotype assigned via value-based matching on computed Phi2 + LEF values between PhotosynQ measurements and Matteo's field data CSV. 9,743 of 13,178 measurements (74%) matched 1:1.

**Computed columns (30):** Same RIDES 2.0 protocol as Aardaker — see Dataset 4. Includes both `Leaf_Temperature_Differenial` (typo in source) and `Leaf_Temperature_Differential`.

**Additional column:** `sample_raw` (VARIANT).

---

## 7. Barley HvDRR — `barley_hvdrr_12922_16934`

|                        |                                                      |
| ---------------------- | ---------------------------------------------------- |
| **Crop**               | Barley                                               |
| **Location**           | MPI Cologne (Y21) & HHU Dusseldorf (Y22), Germany    |
| **Year**               | 2021–2022                                            |
| **Measurements**       | 10,762                                               |
| **Genotypes**          | 641 F3 genotypes, 9 populations (77% coverage)       |
| **Owner**              | Benjamin Stich (Julius Kuhn Institute)               |
| **Protocols**          | Photosynthesis RIDES (Y21) + PSII measurements (Y22) |
| **PhotosynQ projects** | 12116, 12922, 16934                                  |

**Experiment:** QTL analysis of photosynthesis traits in HvDRR (Hordeum vulgare Diverse Resources for Resistance) F3 populations. Nine bi-parental crosses (HvDRR02, HvDRR25, HvDRR27, HvDRR31, HvDRR32, HvDRR34, HvDRR35, HvDRR40) plus inbred parental lines. Two years measured with different protocols:

- **2021 (MPI Cologne):** Photosynthesis RIDES protocol — actinic light = ambient PAR. Includes ECS, PSI, P700 parameters.
- **2022 (HHU Dusseldorf):** PSII measurements protocol — actinic light = 1500 umol/m2/s. PSII fluorescence only. ECS/PSI/P700 columns are NULL.

| Project | Year | Location       | Protocol | Measurements |
| ------- | ---- | -------------- | -------- | ------------ |
| 12116   | 2021 | MPI Cologne    | RIDES    | 2,495        |
| 12922   | 2021 | MPI Cologne    | RIDES    | 2,392        |
| 16934   | 2022 | HHU Dusseldorf | PSII     | 5,872        |

**Excluded measurements (2,490 NULL genotype):** 13 additional barley inbred lines not part of the HvDRR study, plus measurements with SPAD < 10 (quality filter by Yanrong Gao).

**Population sizes:**

| Population | Measurements |
| ---------- | ------------ |
| HvDRR31    | 2,117        |
| HvDRR27    | 1,361        |
| HvDRR25    | 1,130        |
| HvDRR02    | 1,071        |
| HvDRR35    | 645          |
| HvDRR34    | 589          |
| Inbred     | 536          |
| HvDRR40    | 536          |
| HvDRR32    | 287          |

**Development stages:** ASP (anthesis + seed production), REP (reproductive), SEP (seed ripening/senescence).

**Computed columns (29):** Union of RIDES + PSII protocols. Same as RIDES 2.0 (see Dataset 4) but without `leaf_thickness`. ECS, PSI, P700, and Leaf Angle columns are NULL for project 16934.

**Additional column:** `sample_raw` (VARIANT).

**Co-authorship condition:** Any manuscript using this data must include Yanrong Gao, Po-Ya Wu, Shizue Matsubara, and Benjamin Stich as co-authors.

---

## 8. Cowpea IITA — `cowpea_iita_measurements` + `cowpea_iita_snp`

|                  |                                |
| ---------------- | ------------------------------ |
| **Crop**         | Cowpea (_Vigna unguiculata_)   |
| **Locations**    | Ibadan, Ikenne, Kano (Nigeria) |
| **Years**        | 2020–2022                      |
| **Measurements** | 3,360                          |
| **Genotypes**    | 112 (98 with SNP markers)      |
| **SNP markers**  | 9,210 DArT-Seq                 |
| **Owner**        | Olakunle Sansa (IITA)          |
| **Design**       | 8x14 Alpha Lattice, 3 reps     |

**Experiment:** Multi-environment drought stress trial on cowpea at three IITA locations in Nigeria. Each genotype was measured before and during drought stress across multiple years, giving 10 environments (location x year x stress condition). Data was collected with MultispeQ devices and pre-processed by IITA — this dataset contains computed phenotype values, not raw measurement traces.

**Environments (336 measurements each):**

| ENV | Location | Year | Condition     |
| --- | -------- | ---- | ------------- |
| 1   | Ibadan   | 2020 | Before Stress |
| 2   | Ibadan   | 2021 | Before Stress |
| 3   | Ikenne   | 2020 | Before Stress |
| 4   | Ikenne   | 2021 | Before Stress |
| 5   | Kano     | 2021 | Before Stress |
| 6   | Kano     | 2022 | Before Stress |
| 7   | Ibadan   | 2020 | During Stress |
| 8   | Ibadan   | 2021 | During Stress |
| 9   | Ikenne   | 2021 | During Stress |
| 10  | Kano     | 2021 | During Stress |

**Phenotype columns (measurements table):**

| Column                         | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| `relative_chlorophyll_content` | SPAD-equivalent relative chlorophyll content                |
| `leaf_angle`                   | Leaf angle (degrees)                                        |
| `leaf_temp_differential`       | Leaf-air temperature differential                           |
| `lef`                          | Linear Electron Flow                                        |
| `npqt`                         | Non-Photochemical Quenching                                 |
| `phi2`                         | Quantum yield of Photosystem II (PhiII)                     |
| `phi_no`                       | Ratio of incoming light lost via non-regulated pathways     |
| `phi_npq`                      | Ratio of incoming light towards non-photochemical quenching |

**SNP table (`cowpea_iita_snp`):** 9,210 DArT-Seq markers across 11 chromosomes (VU01–VU11) for 98 genotypes. Genotype calls are biallelic (e.g., AA, AC, CC, NN).

**Note:** Unlike the other datasets, the cowpea data has no `sample_raw` VARIANT column — the raw MultispeQ traces are not available.

---

## Protocol Reference

Three MultispeQ measurement protocols are used across the datasets:

### UNZA_PIRK_DIRK_LightPotential_14

**Used by:** Potato Grebbedijk, Bean GART, Barley QTL

Measures PSII fluorescence under both ambient and saturating (high) actinic light. Key innovation is the **light potential** metric — `LEF_light_potential = LEF_high - LEF_ambient` — indicating how much additional electron transport capacity a leaf has beyond current conditions. Also captures **PIRK** (Post-Illumination Rise in fluorescence Kinetics), related to cyclic electron flow around PSI. Includes autogain calibration values for quality assessment.

**25 computed values** including dual-light Phi2/LEF, PIRK amplitudes, autogain parameters.

### Photosynthesis RIDES 2.0

**Used by:** Aardaker Nergena, Barley iMAGIC

The RIDES (Rapid Identification of Differential Efficiency of photosynthesis from Spectra) protocol provides the most comprehensive photosynthesis characterization. Measures under ambient light to preserve the natural state of the photosynthetic apparatus. Captures:

- **PSII fluorescence:** Phi2, NPQt, qL, and derived parameters
- **ECS (Electrochromic Shift):** Thylakoid proton motive force (`ECSt_mAU`), proton conductance (`gH+`), proton flux (`vH+`)
- **PSI redox state:** Active, open, over-reduced, and oxidized PSI centers
- **P700 kinetics:** Dark-interval relaxation kinetics of P700 (`P700_DIRK_ampl`, `kP700`, `tP700`)
- **Morphology:** Leaf angle and leaf thickness

**30 computed values** spanning the full photosynthetic electron transport chain.

### Photosynthesis RIDES (v1) + PSII measurements

**Used by:** Barley HvDRR

Two related protocols used across years. Year 1 (RIDES) captures the full parameter set including ECS, PSI, and P700. Year 2 (PSII measurements) uses fixed high actinic light (1500 umol/m2/s) and captures only PSII fluorescence parameters. When combined, ECS/PSI/P700 columns are NULL for Year 2 measurements.

**29 computed values** (union of both protocols).
