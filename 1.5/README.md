# Intel vaizdų analizė — transfer learning, klasifikacija, objektų aptikimas ir segmentavimas

VILNIUS TECH kurso *Gilusis mokymas* darbas: suprasti pateiktus notebookus ir pritaikyti juos **kitiems vaizdų duomenims**. Abu užrašai naudoja **Intel Image Classification** rinkinį: pirmame mokomas scenų klasifikatorius, antrame viena nuotrauka analizuojama iš anksto išmokytais modeliais. Notebookų tekstai yra anglų kalba, README — lietuvių.

| **Užrašas** | **Failas** | **Originalas** |
| --- | --- | --- |
| EfficientNetV2B1 + klasifikatorius + augmentacija | [`cnn_Transfer_learning_Intel.ipynb`](cnn_Transfer_learning_Intel.ipynb) | `cnn_Transfer_learning.ipynb` |
| Vieno vaizdo klasifikacija + objektų aptikimas + segmentavimas | [`cnn_One_Image_Intel.ipynb`](cnn_One_Image_Intel.ipynb) | `cnn_One_Image.ipynb` |

## Transfer learning: kas replikuota

Pradinis užrašas — `cnn_Transfer_learning.ipynb`, naudojantis **CIFAR-10**: 32 × 32 RGB vaizdus ir 10 klasių. Originale duomenys įkeliami per Hugging Face `load_dataset("uoft-cs/cifar10")`, o Keras atsisiuntimo variantas paliktas užkomentuotas.

Išlaikyta pagrindinė darbo eiga: duomenų įkėlimas → vaizdų paruošimas → iš anksto išmokyto modelio naudojimas požymiams išgauti → naujo klasifikatoriaus mokymas → vertinimas → mokymas su augmentacija → rezultatų palyginimas.

Tai adaptacija, o ne identiška originalo kopija. Pakeistas duomenų įkėlimas, modelio API, normalizavimas ir eksperimentų palyginimo tvarka:

- Vietoj TensorFlow Hub `efficientnet_v2_imagenet21k_b1` naudojamas `tf.keras.applications.EfficientNetV2B1` su **ImageNet (1000 klasių)** svoriais.
- Visas modelis kuriamas per `tf.keras`, nemaišant `tf_keras` ir TensorFlow Hub sluoksnių.
- EfficientNet bazė lieka užšaldyta; mokomas tik šešių klasių klasifikatorius. Bazės fine-tuning neatliekamas.
- Modeliai be augmentacijos ir su augmentacija pradedami nuo **tų pačių pradinių svorių**. Antras eksperimentas nėra pirmojo modelio mokymo tęsinys.
- Modelis pasirenkamas pagal validacijos nuostolį; testavimo duomenys paliekami galutiniam vertinimui.

## Duomenų rinkinys ir šaltinis

Naudojamas **Intel Image Classification** — gamtos ir miesto scenų RGB nuotraukos. Transfer learning notebooke vaizdai keičiami į **240 × 240**. Vieno vaizdo notebooke pasirenkama viena `seg_test` nuotrauka; klasifikatoriams ji paruošiama kaip **384 × 384** vaizdas su proporcijas išlaikančiu užpildymu.

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

Transfer learning notebooke duomenys skaitomi partijomis per `tf.data`, nekeliant visų paruoštų vaizdų į RAM. Pikselių reikšmės paliekamos **0–255** intervale, nes pasirinkto EfficientNetV2 modelio normalizavimas yra integruotas. Papildomas dalijimas iš 255 neatliekamas.

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

## Transfer learning rezultatai

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

## Vieno vaizdo analizė — `cnn_One_Image_Intel.ipynb`

Antras užrašas pritaikytas iš `cnn_One_Image.ipynb`. Išlaikyti originalūs modeliai ir trys dalys: **klasifikacija → objektų aptikimas → segmentavimas**. Vietoj originale pateiktų internetinių nuotraukų pasirenkamas vaizdas iš Intel rinkinio. Modeliai šiame notebooke papildomai nemokomi.

### Kas pakeista ir kas išlaikyta

| **Dalis** | **Ši versija** |
| --- | --- |
| Duomenys | Viena pasirinktos klasės nuotrauka iš `seg_test`; numatyta `street`, `image_index = 0` |
| Nuotraukos pasirinkimas | `image_name`, `image_index`, pasirinktinai `LOCAL_DATA_DIR` arba `LOCAL_IMAGE_PATH` |
| Klasifikacijos modelis 1 | Originalus TensorFlow Hub EfficientNetV2-S, išmokytas su ImageNet-21k |
| Klasifikacijos modelis 2 | Originalus TensorFlow Hub EfficientNetV2-S, ImageNet-21k → ImageNet-1k |
| Objektų aptikimas | Originalus SSD MobileNetV2, išmokytas su Open Images V4 |
| Segmentavimas | Originalus HRNetV2-W48, išmokytas su ADE20K |
| Vaizdų paruošimas | RGB, `float32`, pikseliai **0–1**; klasifikacijai 384 × 384 su užpildymu |
| Iškarpa | Viršutinis kairysis kampas nurodomas procentais; dydis — trumpesnės vaizdo kraštinės procentais |
| Numatyta iškarpa | `x = 20`, `y = 20`, `crop_size_percent = 60` |
| Rezultatų pateikimas | Abiejų klasifikatorių top-4, objektų rėmeliai, segmentavimo atsako žemėlapiai ir keturios perdangos |

Šio notebooko **0–1** normalizavimas skirtas originaliems TensorFlow Hub modeliams. Jis skiriasi nuo transfer learning notebooko Keras EfficientNetV2 įvesties **0–255** intervale.

Intel aplankų pavadinimai aprašo vaizdų šaltinį, tačiau nekeičia modelių išėjimų: klasifikatoriai naudoja ImageNet klases, detektorius — Open Images, segmentavimo modelis — ADE20K. Todėl, pavyzdžiui, šis notebookas neapriboja klasifikacijos iki šešių Intel scenų klasių.

### Klasifikacijos rezultatai

Pateiktame gatvės vaizdo pavyzdyje gautos šios prognozės. Lentelėse palikti modelių klasių ID ir originalūs angliški pavadinimai.

**Modelis 1 — ImageNet-21k**

| **Vieta** | **Klasės ID** | **Klasė** | **Softmax reikšmė `p`** |
| --- | --- | --- | --- |
| 1 | 10880 | `street` | 0.1005 (10,05 %) |
| 2 | 5125 | `building, edifice` | 0.0886 (8,86 %) |
| 3 | 11410 | `tramline, tramway, streetcar_track` | 0.0590 (5,90 %) |
| 4 | 10879 | `street` | 0.0301 (3,01 %) |

**Modelis 2 — ImageNet-1k**

| **Vieta** | **Klasės ID** | **Klasė** | **Softmax reikšmė `p`** |
| --- | --- | --- | --- |
| 1 | 743 | `prison` | 0.0892 (8,92 %) |
| 2 | 860 | `tobacco shop` | 0.0517 (5,17 %) |
| 3 | 698 | `palace` | 0.0407 (4,07 %) |
| 4 | 675 | `moving van` | 0.0300 (3,00 %) |

ImageNet-21k modelio pirmos prognozės semantiškai dera su gatvės ir pastatų vaizdu. ImageNet-1k modelis siūlo konkretesnes objektų ar pastatų kategorijas; vien iš šių prognozių negalima patvirtinti, kad nuotraukoje yra kalėjimas ar tabako parduotuvė. Didžiausios abiejų modelių reikšmės nedidelės, todėl prognozės nėra aiškiai sutelktos į vieną klasę.

`p` yra konkretaus modelio softmax išėjimas, **ne viso rinkinio tikslumas**. Kadangi modeliai naudoja skirtingus klasių rinkinius, jų `p` reikšmės nėra tiesioginis tarpusavio kokybės matas. Du `street` įrašai turi skirtingus ID ir pateiktoje išvestyje išlaikomi atskirai.

### Objektų aptikimas

SSD MobileNetV2 taikomas visai pradinei nuotraukai ir jos iškarpai. Notebookas pateikia objektų pavadinimus, įverčius ir rėmelius; numatytas slenkstis `min_score = 0.25`, rodoma iki 20 aptikimų. Pateiktoje rezultatų medžiagoje nėra detektoriaus išvesties, todėl aptiktų objektų skaičius ir jų rezultatai čia nenurodomi.

### Segmentavimo rezultatai

HRNet modelis analizuojamai iškarpai pateikia atskirų klasių atsako žemėlapius. Pateiktame tinklelyje matomas **151 kanalas**: fonas ir 150 ADE20K klasių.

![HRNet klasių atsako žemėlapiai](assets/one_image_hrnet_response_maps.png)

Keturių pasirinktų kanalų perdangos: `2: building`, `5: tree`, `13: person`, `18: plant`.

![Pastato, medžio, žmogaus ir augalo kanalų perdangos](assets/one_image_hrnet_overlays.png)

`building` kanalo ryškesnis atsakas apima didelę matomų fasadų dalį. Kitų trijų pasirinktų kanalų atsakai labiau lokalūs. Tai klasės atsako vizualizacijos, o ne anotacijomis patvirtintos objektų vietos ar galutinė kiekvienam pikseliui priskirtų klasių kaukė. Vien ryškumo skirtinguose grafikuose negalima laikyti tiesioginiu klasių tikimybių palyginimu, nes kiekvienas žemėlapis atvaizduojamas su automatiniu spalvų masteliu.

Intel rinkinyje nėra objektų rėmelių ar segmentavimo kaukių anotacijų. Dėl to šiame pavyzdyje neatliekamas kiekybinis aptikimo ar segmentavimo vertinimas, pvz., mAP ar IoU skaičiavimas.

## Kaip paleisti

### Transfer learning notebookas

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

### Vieno vaizdo notebookas

Atidaryti [`cnn_One_Image_Intel.ipynb`](cnn_One_Image_Intel.ipynb) Colab ir vykdyti langelius iš eilės. Pirmas vykdomasis langelis įdiegia `tensorflow`, `tensorflow-hub`, `tf-keras`, `kagglehub`, `requests`, `pillow` ir `matplotlib`. Internetas reikalingas duomenims, modeliams ir klasių etiketėms atsisiųsti.

Vietiniam paleidimui:

```bash
jupyter notebook cnn_One_Image_Intel.ipynb
```

Nuotraukos pasirinkimo langelyje:

```python
image_name = 'street'  # buildings, forest, glacier, mountain, sea, street
image_index = 0
LOCAL_DATA_DIR = None
LOCAL_IMAGE_PATH = None
```

Galima nurodyti jau išpakuoto rinkinio kelią per `LOCAL_DATA_DIR`. Norint naudoti savo nuotrauką, nurodyti `LOCAL_IMAGE_PATH`; tuomet Intel rinkinio atsisiuntimas praleidžiamas. Jei Kaggle prašo prisijungti, naudoti `kagglehub.login()` arba vietinę duomenų kopiją.

Pakeitus nuotrauką, pakartotinai vykdyti jos įkėlimo, iškarpos ir tolesnius analizės langelius. Mokymo ir epochų nustatymų šiame notebooke nėra. Jis nepriklauso nuo pirmo notebooko išsaugotų `.keras` modelių.

## Išsaugomi failai

Transfer learning notebookas po vykdymo sukuria katalogą `intel_results`:

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

Vieno vaizdo notebookas rezultatus rodo langelių išvestyse; atskirų rezultatų failų automatiškai nekuria. Šio README iliustracijos saugomos kataloge `assets/`, kurį reikia laikyti kartu su README.

## Šaltiniai

- Originalūs pateikti užrašai: `cnn_Transfer_learning.ipynb` ir `cnn_One_Image.ipynb`.
- Vieno vaizdo klasifikacijos skaičiai ir HRNet iliustracijos — pateiktos vykdymo išvestys.
- [Intel Image Classification — Kaggle](https://www.kaggle.com/datasets/puneet6060/intel-image-classification).
- [Keras EfficientNetV2 dokumentacija](https://keras.io/api/applications/efficientnet_v2/).
- [Kagglehub: duomenų atsisiuntimas](https://github.com/Kaggle/kagglehub).
- [TensorFlow Hub objektų aptikimo pavyzdys](https://www.tensorflow.org/hub/tutorials/object_detection).
- [TensorFlow Hub HRNet segmentavimo pavyzdys](https://www.tensorflow.org/hub/tutorials/hrnet_semantic_segmentation).
