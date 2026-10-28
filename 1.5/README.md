# Scenų klasifikacija — TensorFlow ir transfer learning

VILNIUS TECH kurso *Gilusis mokymas* darbas: suprasti pateiktą transfer learning notebooką ir pritaikyti jį **kitam vaizdų duomenų rinkiniui**. Šioje versijoje CIFAR-10 pakeistas **Intel Image Classification** rinkiniu.

| **Užrašas** | **Failas** | **Originalas** |
| --- | --- | --- |
| EfficientNetV2B1 + klasifikatorius + augmentacija | [`cnn_Transfer_learning_Intel.ipynb`](cnn_Transfer_learning_Intel.ipynb) | `cnn_Transfer_learning.ipynb` |

## Kas replikuota

Pradinis užrašas — `cnn_Transfer_learning.ipynb`, naudojantis **CIFAR-10**: 32 × 32 RGB vaizdus ir 10 klasių. Originale duomenys įkeliami per Hugging Face `load_dataset("uoft-cs/cifar10")`, o Keras atsisiuntimo variantas paliktas užkomentuotas.

Išlaikyta pagrindinė darbo eiga: duomenų įkėlimas → vaizdų paruošimas → iš anksto išmokyto modelio naudojimas požymiams išgauti → naujo klasifikatoriaus mokymas → vertinimas → mokymas su augmentacija → rezultatų palyginimas.

Tai adaptacija, o ne identiška originalo kopija. Pakeistas duomenų įkėlimas, modelio API, normalizavimas ir eksperimentų palyginimo tvarka:

- Vietoj TensorFlow Hub `efficientnet_v2_imagenet21k_b1` naudojamas `tf.keras.applications.EfficientNetV2B1` su **ImageNet (1000 klasių)** svoriais.
- Visas modelis kuriamas per `tf.keras`, nemaišant `tf_keras` ir TensorFlow Hub sluoksnių.
- EfficientNet bazė lieka užšaldyta; mokomas tik šešių klasių klasifikatorius. Bazės fine-tuning neatliekamas.
- Modeliai be augmentacijos ir su augmentacija pradedami nuo **tų pačių pradinių svorių**. Antras eksperimentas nėra pirmojo modelio mokymo tęsinys.
- Modelis pasirenkamas pagal validacijos nuostolį; testavimo duomenys paliekami galutiniam vertinimui.

## Duomenų rinkinys ir šaltinis

Naudojamas **Intel Image Classification** — gamtos ir miesto scenų RGB nuotraukos. Vaizdai prieš perduodant modeliui sumažinami arba padidinami iki **240 × 240**.

| | **Aprašymas** |
| --- | --- |
| Šaltinis | [Intel Image Classification — Kaggle](https://www.kaggle.com/datasets/puneet6060/intel-image-classification) |
| Klasės | `buildings`, `forest`, `glacier`, `mountain`, `sea`, `street` |
| Klasių reikšmės | Pastatai, miškas, ledynas, kalnai, jūra, gatvė |
| Pažymėti duomenys | 14 034 vaizdai `seg_train` ir 3 000 vaizdų `seg_test` |
| Mokymo ir validacijos padalijimas | 11 227 mokymo + 2 807 validacijos vaizdai; 80/20 iš `seg_train`, `stratify`, `seed=42` |
| Galutinis testas | Atskiras `seg_test`: 3 000 vaizdų |
| Papildomas aplankas | `seg_pred`: vaizdai be etikečių, nenaudojami tikslumui skaičiuoti |
| Atsisiuntimas | `kagglehub.dataset_download("puneet6060/intel-image-classification")` arba vietinis išpakuotas rinkinys |

Duomenys skaitomi partijomis per `tf.data`, nekeliant visų paruoštų vaizdų į RAM. Pikselių reikšmės paliekamos **0–255** intervale, nes pasirinkto EfficientNetV2 modelio normalizavimas yra integruotas. Papildomas dalijimas iš 255 neatliekamas.

## CIFAR-10 → Intel Image Classification atitikimas

| **Originalas (CIFAR-10)** | **Ši versija (Intel)** | **Pastaba** |
| --- | --- | --- |
| 10 objektų klasių | 6 scenų klasės | Kitas duomenų rinkinys ir klasifikavimo sritis |
| 32 × 32 RGB, modelyje padidinama iki 240 × 240 | Vaizdai įkeliant keičiami į 240 × 240 RGB | Modelis gauna vienodo dydžio įvestį |
| Hugging Face CIFAR-10 | Kaggle Intel, duomenų aplankai | Galima naudoti ir vietinę kopiją |
| Pikseliai dalijami iš 255 | Pikseliai 0–255, normalizavimas modelyje | Pritaikyta Keras EfficientNetV2 reikalavimams |
| TensorFlow Hub EfficientNetV2 B1, ImageNet-21k | Keras EfficientNetV2B1, ImageNet | Pasikeitė iš anksto išmokytų svorių šaltinis |
| `Dense(10)`, logitai | `Dense(6, activation="softmax")` | `sparse_categorical_crossentropy`, be `from_logits=True` |
| Testo duomenys naudojami ir validacijai | Atskiri mokymo, validacijos ir testo rinkiniai | Testas nenaudojamas modelio pasirinkimui |
| Augmentacija taikoma prieš papildomą mokymą | Atskirai mokomas modelis su dinamine augmentacija | Abu variantai pradeda nuo tų pačių svorių |
| Modelio katalogas ir ZIP | `.keras` modeliai ir `metadata.json` | Nereikia `zip`, `unzip` ar `rm` komandų |

## Modelis ir mokymo nustatymai

Architektūra: **240 × 240 × 3 → EfficientNetV2B1 → global average pooling → Dense(6, softmax)**. Variantas su augmentacija prieš EfficientNet bazę papildomai transformuoja vaizdus.

| **Nustatymas** | **Reikšmė** |
| --- | --- |
| Bazinis modelis | EfficientNetV2B1, `weights="imagenet"`, `include_top=False`, `pooling="avg"` |
| Mokomi sluoksniai | Tik paskutinis Dense klasifikatorius |
| Optimizatorius | Adam, mokymosi greitis `0.001` |
| Nuostolio funkcija | `sparse_categorical_crossentropy` |
| Partijos dydis | 32 |
| Atsitiktinumo sėkla | 42 |
| Pateiktas eksperimentas | 10 epochų kiekvienam variantui |
| Geriausio kontrolinio taško kriterijus | Mažiausias `val_loss` |
| Ankstyvas stabdymas | `EarlyStopping`, `patience=3`, geriausių svorių atkūrimas |

**Epochų pastaba:** pridėtame notebooke numatyta `EPOCHS = 5`, o toliau pateikti vykdymo rezultatai yra iš **10 epochų** eksperimento. Norint paleisti tokios pačios trukmės eksperimentą, nustatymų langelyje reikia įrašyti `EPOCHS = 10`. Ankstyvas stabdymas gali užbaigti mokymą anksčiau.

Augmentacija: horizontalus atspindėjimas, nedidelis pasukimas (`0.05`), poslinkis (`0.1` abiem kryptimis), mastelio keitimas (`0.1`) ir šviesumo keitimas (`0.1`, pikselių intervalas 0–255). Ji įjungta tik mokymo metu. Vertikalūs atspindžiai nenaudojami.

## Rezultatai

Toliau pateikti rezultatai paimti iš pateiktos **10 epochų vykdymo išvesties**. Jie nėra naujo README rengimo metu atlikto mokymo rezultatai. Vykdymo įrenginys ir bibliotekų versijos pateiktoje išvestyje nenurodyti.

Vienodai atsitiktinai spėjant vieną iš šešių klasių, tikėtinas tikslumas būtų apie **16,67 %**.

| **Modelis** | **Epochos** | **Testo tikslumas** | **Testo nuostolis** |
| --- | --- | --- | --- |
| Be augmentacijos (`baseline`) | 10 | **0.9290 (92,90 %)** | **0.1855** |
| Su augmentacija (`augmented`) | 10 | 0.9223 (92,23 %) | 0.2048 |

Šiame eksperimente modelis be augmentacijos pasiekė **0,67 procentinio punkto** didesnį testo tikslumą. Augmentacija pagerėjimo nesuteikė. Tai vieno eksperimento rezultatas; bendresnei išvadai reikėtų kelių pakartojimų.

### Mokymo ir validacijos palyginimas

| **Modelis** | **10-os epochos mokymo tikslumas** | **10-os epochos validacijos tikslumas** | **Didžiausias validacijos tikslumas per mokymą** | **Mažiausias validacijos nuostolis** |
| --- | --- | --- | --- | --- |
| Be augmentacijos | 0.9483 | 0.9252 | 0.9266 | **0.1967** |
| Su augmentacija | 0.9270 | 0.9248 | 0.9266 | 0.2035 |

Abu variantai pasiekė tokį patį didžiausią validacijos tikslumą, tačiau bazinis modelis turėjo mažesnį minimalų validacijos nuostolį. Pagal notebooko pasirinkimo taisyklę pasirenkamas **`baseline`**. Galutinis testas vertina geriausius pagal `val_loss` išsaugotus kontrolinius taškus, todėl jo rezultatai nesusieti vien su paskutinės epochos svoriais.

### Pasirinkto modelio klasifikavimo ataskaita

Pateikta ataskaita atitinka bazinį modelį; metrikos suapvalintos kaip vykdymo išvestyje.

| **Klasė** | **Precision** | **Recall** | **F1-score** | **Testo vaizdų skaičius** |
| --- | --- | --- | --- | --- |
| `buildings` | 0.94 | 0.92 | 0.93 | 437 |
| `forest` | 1.00 | 1.00 | 1.00 | 474 |
| `glacier` | 0.87 | 0.88 | 0.88 | 553 |
| `mountain` | 0.89 | 0.86 | 0.88 | 525 |
| `sea` | 0.97 | 0.98 | 0.97 | 510 |
| `street` | 0.92 | 0.95 | 0.94 | 501 |
| **Macro avg** | **0.93** | **0.93** | **0.93** | **3 000** |
| **Weighted avg** | **0.93** | **0.93** | **0.93** | **3 000** |

Geriausiai atpažįstami miško vaizdai. Mažesnės F1 reikšmės gautos ledynų ir kalnų klasėms. Norint nustatyti, kurias klases modelis painioja tarpusavyje, reikia peržiūrėti notebooko sugeneruotą klaidų matricą.

## Kaip paleisti

Atidaryti [`cnn_Transfer_learning_Intel.ipynb`](cnn_Transfer_learning_Intel.ipynb) Google Colab, pasirinkti GPU aplinką ir vykdyti *Runtime → Run all*. Notebooko aprašai, kodas ir grafikų užrašai yra anglų kalba.

Pirmas langelis įdiegia `tensorflow`, `kagglehub`, `matplotlib`, `scikit-learn` ir `pillow`. Reikalingas internetas duomenims ir ImageNet svoriams atsisiųsti. Jei Kaggle prašo autentifikacijos, galima naudoti `kagglehub.login()` arba atsisiųsti ir išpakuoti duomenis rankiniu būdu.

Vietiniam paleidimui reikia Jupyter ir Python aplinkos, kurią palaiko TensorFlow. Iš katalogo, kuriame yra notebookas:

```bash
jupyter notebook cnn_Transfer_learning_Intel.ipynb
```

Jei duomenys jau išpakuoti, notebooke nustatyti:

```python
LOCAL_DATA_DIR = r"D:\data\intel-image-classification"
```

Norint kartoti čia aprašytą 10 epochų eksperimentą:

```python
EPOCHS = 10
```

Pritrūkus GPU atminties, `BATCH_SIZE` sumažinti iki 16 arba 8. Tikslūs rezultatai gali skirtis priklausomai nuo vykdymo aplinkos ir bibliotekų versijų.

## Išsaugomi failai

Notebookas po vykdymo sukuria katalogą `intel_results`:

| **Failas** | **Paskirtis** |
| --- | --- |
| `baseline.keras` | Geriausias modelis be augmentacijos pagal `val_loss` |
| `augmented.keras` | Geriausias modelis su augmentacija pagal `val_loss` |
| `intel_best.keras` | Pagal validacijos nuostolį pasirinktas modelis |
| `metadata.json` | Klasių tvarka, vaizdo dydis, mokymo nustatymai ir vertinimo metrikos |
| `classification_report.txt` | Pasirinkto modelio klasifikavimo ataskaita |
| `learning_curves.png` | Abiejų modelių mokymo ir validacijos kreivės |
| `confusion_matrix.png` | Pasirinkto modelio klaidų matrica |
| `sample_predictions.png` | Testo vaizdų ir prognozių pavyzdžiai |

Naudojant Colab, reikiamus modelius ir rezultatų failus reikia atsisiųsti prieš baigiant sesiją. Paskutinis vykdomasis notebooko langelis leidžia patikrinti išsaugotą modelį su savo nuotrauka, nurodžius `MY_IMAGE_PATH`.

## Šaltiniai

- Originalus pateiktas užrašas: `cnn_Transfer_learning.ipynb`.
- [Intel Image Classification — Kaggle](https://www.kaggle.com/datasets/puneet6060/intel-image-classification).
- [Keras EfficientNetV2 dokumentacija](https://keras.io/api/applications/efficientnet_v2/).
- [Kagglehub: duomenų atsisiuntimas](https://github.com/Kaggle/kagglehub).
