# 1.3 Bank Marketing — TensorFlow neuroninis tinklas

VILNIUS TECH kurso *Gilusis mokymas* užduotis 1.3: suprasti dėstytojo Colab užrašus ir perdaryti juos su kitais verslo duomenimis.

## Kas replikuota

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

Klasės disbalansas: apie **11,3 %** teigiamų (`yes`). Mokant naudotas `class_weight`; šalia Keras `accuracy` skaičiuojamas AUC.

| Metrika | Testo aibė (10 %) |
| --- | --- |
| Tikslumas (sigmoidė, slenkstis 0,5) | *bus įrašyta po užrašų vykdymo* |
| AUC | *bus įrašyta po užrašų vykdymo* |

Užrašai su išsaugotais išėjimais: [`BankMarketing_NN.ipynb`](BankMarketing_NN.ipynb).

## Kaip paleisti

Python 3 su `tensorflow`, `pandas`, `scikit-learn`. Iš šio katalogo:

```bash
jupyter notebook BankMarketing_NN.ipynb
```

arba Colab: atidaryti `BankMarketing_NN.ipynb` ir *Runtime → Run all*. Vietinis CSV nereikalauja Kaggle paskyros.
