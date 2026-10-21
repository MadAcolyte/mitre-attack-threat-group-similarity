# 1.3 Bank Marketing — TensorFlow NN ir Decision Forests

VILNIUS TECH kurso *Gilusis mokymas* užduotis 1.3: suprasti dėstytojo Colab užrašus ir perdaryti **abu** su kitais verslo duomenimis.

| Užrašas | Failas | Originalas |
| --- | --- | --- |
| Neuroninis tinklas | [`BankMarketing_NN.ipynb`](BankMarketing_NN.ipynb) | [AdventureWorks DW using TensorFlow Neural Network](https://colab.research.google.com/drive/1LLFM2Ba5jAZSna8JnS44frwSLW9mx5As) |
| Atsitiktinis miškas | [`BankMarketing_DF.ipynb`](BankMarketing_DF.ipynb) | [AdventureWorks DW using TensorFlow Decision Forests](https://colab.research.google.com/drive/1zE7b6UlSOreWsgD7lGQOVfEki_xTRDAX) |

## Kas replikuota (neuroninis tinklas)

Dėstytojo užrašai **AdventureWorks DW using TensorFlow Neural Network** (`AdventureWorksDW_NN.ipynb`, Algirdas Laukaitis).

- Colab: <https://colab.research.google.com/drive/1LLFM2Ba5jAZSna8JnS44frwSLW9mx5As>
- Originalo CSV: [`vTargetMail.csv`](https://raw.githubusercontent.com/aalgirdas/AdventureWorksDW/main/vTargetMail.csv) (18 484 eilutės, 32 stulpeliai, žymė `BikeBuyer`)

Langeliai ir skyriai (1.1–1.4, 2, 3, 4 ir inferencija) eina ta pačia tvarka: CSV → valymas → 80:10:10 padalijimas → `tf.data` (`df_to_dataset`, paketas 256) → Keras `StringLookup` / `IntegerLookup` + `CategoryEncoding` ir `Normalization` → `Dense(64, relu)` → `Dense(32, relu)` → `Dense(1)` → `adam` + `BinaryCrossentropy(from_logits=True)` → 30 epochų → testas → vieno kliento prognozė.

## Duomenų rinkinys ir šaltinis

Naudojamas **UCI Bank Marketing** (`bank-additional-full.csv`): Portugalijos banko telefono kampanijos, tikslas — numatyti, ar klientas užsisakys terminuotą indėlį (`y`: `yes` / `no`).

| | |
| --- | --- |
| Failas | [`data/bank-additional-full.csv`](data/bank-additional-full.csv) (vietinė kopija, ~5,6 MB, 41 188 eilutės) |
| Oficialus šaltinis | [UCI dataset 222 — Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) |
| Atsisiuntimas be Kaggle | <https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip> |
| Citatavimas | S. Moro, P. Cortez, P. Rita. *A Data-Driven Approach to Predict the Success of Bank Telemarketing.* Decision Support Systems, 62:22–31, 2014. |

Užrašai pirma skaito vietinį CSV (`sep=';'`). Jei failo nėra (pvz. atidarius tik Colab), jie patys atsisiunčia tą patį UCI zip.

`duration` **išmetamas**: tai paskutinio skambučio trukmė, žinoma tik po pokalbio ir stipriai nutekinanti žymę `y`.

## Stulpelių atitikimas (AdventureWorks → Bank Marketing)

| AdventureWorks (`vTargetMail`) | Bank Marketing | Pastaba |
| --- | --- | --- |
| `BikeBuyer` → `target` | `y` → `target` (0/1) | Dviračio pirkimas vs. terminuoto indėlio sutikimas |
| `Age` | `age` | Kliento amžius |
| `MaritalStatus` | `marital` | Šeimyninė padėtis |
| `EnglishEducation` | `education` | Išsilavinimas |
| `EnglishOccupation` | `job` | Profesija / darbas |
| `HouseOwnerFlag` | `housing` | Originalas — ar turi namą; čia — ar turi būsto paskolą |
| `Gender` | — | Tiesioginio analogo nėra |
| `YearlyIncome` | `emp_var_rate`, `euribor3m`, `nr_employed`, `cons_price_idx`, `cons_conf_idx` | Pajamų stulpelio nėra; naudojami makroekonominiai rodikliai |
| `TotalChildren`, `NumberChildrenAtHome`, `NumberCarsOwned` | — | Šeimos / turto analogų nėra |
| `Region` | `month`, `contact` | Geografijos nėra; kampanijos kontekstas (mėnuo, kontakto tipas) |
| `CommuteDistance` | `campaign`, `pdays`, `previous`, `poutcome` | Ne atstumas, o ankstesni kontaktai |
| Identifikatoriai (raktai, vardai, adresas, telefonas) | `duration` | Originalas metė ID; čia metame `duration` dėl nutekėjimo |

Papildomai paliekami Bank Marketing kategoriniai požymiai `default`, `loan`, `day_of_week`.

## Rezultatai

Klasės disbalansas: **11,3 %** teigiamų (`yes`) visame rinkinyje (teste 11,8 %). Mokant naudotas `class_weight`. Grynas Keras `BinaryAccuracy` čia matuoja slenkstį ant logitų, todėl ataskaitoje naudojame tikimybę po `sigmoid`.

| Metrika | Testo aibė (10 %, 4119 eilutės) |
| --- | --- |
| Tikslumas (sigmoidė, slenkstis 0,5) | **0.8424** (84,2 %) |
| AUC | **0.7848** |
| Keras `evaluate` accuracy / AUC | 0.8691 / 0.7848 |

Vieno pavyzdinio kliento (35 m., `admin.`, universitetinis išsilavinimas, `cellular`, be ankstesnių kampanijų) indėlio tikimybė: **21,2 %**.

Užrašai su išsaugotais išėjimais: [`BankMarketing_NN.ipynb`](BankMarketing_NN.ipynb).

## Kas replikuota (Decision Forests)

Dėstytojo užrašai **AdventureWorks DW using TensorFlow Decision Forests** (`AdventureWorksDW_Decision Forests.ipynb`, Algirdas Laukaitis).

- Colab: <https://colab.research.google.com/drive/1zE7b6UlSOreWsgD7lGQOVfEki_xTRDAX>

Langeliai 1.1–5 ta pačia tvarka: CSV → eilutės peržiūra → `duration` išmetimas ir `y` → `target` → **90:10** mokymas/testas **be validacijos** (OOB atstoja validaciją) → `tfdf.keras.pd_dataframe_to_tf_dataset` → `RandomForestModel(num_trees=10, max_depth=15)` → `fit` / `evaluate` (accuracy + AUC) → OOB kreivės (accuracy ir logloss pagal medžių skaičių) → vieno medžio piešinys (`tfdf.model_plotter`) → SavedModel ir prognozė tam pačiam pavyzdiniam klientui.

**TF-DF versijos.** Užrašai diegia `tensorflow_decision_forests` (čia 1.12.0 su TensorFlow 2.19.0). TF 2.19 deklaruoja `protobuf<6`, o TF-DF 1.12 / `ydf` 0.16 sugeneruotas su Protobuf 6.31.1; jei importas krenta, užrašai pin'ina `protobuf==6.31.1`.

Užrašai su išsaugotais išėjimais: [`BankMarketing_DF.ipynb`](BankMarketing_DF.ipynb).

## NN ir Random Forest palyginimas

Abu modeliai naudoja tą patį UCI Bank Marketing rinkinį be `duration` ir **tą patį 10 % testą** (`random_state=42`; NN validacija paimta iš RF mokymo 90 %). RF mokomas iš visų 90 %, NN — iš 80 % + 10 % validacija. RF `num_trees=10` (kaip originale), NN — 30 epochų `Dense(64)–Dense(32)–Dense(1)`.

| | NN | Random Forest |
| --- | --- | --- |
| Tikslumas (slenkstis 0,5) | **0.8424** | **0.8932** (Keras `evaluate`: 0.8956) |
| AUC | **0.7848** | **0.759** |
| Požymių paruošimas | `StringLookup` + `CategoryEncoding`, `Normalization` | TF-DF pats atpažįsta tipus |
| Validacija | atskira 10 % aibė | out-of-bag |
| Klasės disbalansas | `class_weight` | be svorių (originalo eiga) |
| Pavyzdinio kliento `P(yes)` | 21,2 % | 0 % (`winner_take_all` balsas) |

RF laimi pagal **tikslumą**, nes be klasės svorių jis dažniau spėja daugumą (`no`; bazė ~88,7 %). NN su `class_weight` geriau **ranguoja** retą `yes` klasę (aukštesnis AUC). Originalo RF naudoja `winner_take_all_inference=True`, todėl `predict` yra klasės balsas (0 arba 1), ne kalibruota tikimybė — todėl pavyzdinis klientas gauna 0 %.

DF OOB tikslumas po 10 medžių: ~0.895.

## Kaip paleisti

Python 3 su `tensorflow`, `pandas`, `scikit-learn`; miškui dar `tensorflow_decision_forests` (ir prireikus `protobuf==6.31.1`). Iš šio katalogo:

```bash
jupyter notebook BankMarketing_NN.ipynb
jupyter notebook BankMarketing_DF.ipynb
```

arba Colab: atidaryti užrašą ir *Runtime → Run all*. Vietinis CSV nereikalauja Kaggle paskyros.
