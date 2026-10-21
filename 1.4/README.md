# 1.4 Konvoliucinis neuroninis tinklas (CNN)

Gilusis mokymas, VILNIUS TECH. Užduotis: suprasti dėstytojo Colab dokumentą ir perdaryti jį su **savo** duomenimis.

## Originalus Colab

- Pavadinimas: **Colab CNN**, autorius Algirdas Laukaitis
- Nuoroda: [https://colab.research.google.com/drive/1wx-OBEcjPhAfv8AZ5Fl59mp7RY5Hm0Ql](https://colab.research.google.com/drive/1wx-OBEcjPhAfv8AZ5Fl59mp7RY5Hm0Ql)
- Originalas **perskaitytas** (atsisiųstas kaip `cnn.ipynb` per Google Drive export, failo ID `1wx-OBEcjPhAfv8AZ5Fl59mp7RY5Hm0Ql`).
- Duomenų rinkinys: **CIFAR-10** (32×32 RGB, 10 klasių: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck). Keras `datasets.cifar10.load_data()` ląstelė pažymėta kaip praleista (atsisiuntimas buvęs lėtas), vietoj to naudotas Hugging Face `load_dataset("uoft-cs/cifar10")`.
- Struktūra (45 ląstelės):
  1. **PART 1** — CIFAR-10 įkėlimas, normalizavimas `/255`, pirmų 100 vaizdų piešimas, CNN (`Conv2D 32 → Pool → Conv2D 64 → Pool → Conv2D 64 → Flatten → Dense 64 → Dense 10`), `adam` + `SparseCategoricalCrossentropy(from_logits=True)`, 20 epochų, tikslumo grafikas (~70 % originale).
  2. **PART 2** — pirmojo konvoliucinio sluoksnio filtrai (2 filtrai × 3 RGB kanalai), požymių žemėlapiai, rankinė `numpy` konvoliucija su bias ir ReLU, palyginimas su Keras.
  3. **PART 3** — daugiasluoksnis perceptronas (MLP) tam pačiam uždaviniui, 15 epochų (~40 % originale), palyginimas su CNN.

## Naujas duomenų rinkinys

- Pavadinimas: **tf_flowers** (`flower_photos`)
- Klasės (5): `daisy`, `dandelion`, `roses`, `sunflowers`, `tulips`
- Šaltinis (viešas, be Kaggle): [https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz](https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz)
- Apimtis: ~3670 JPEG nuotraukų; čia keičiama į **32×32 RGB**, dalijama 80/20 (`seed=42`)
- Kodėl šis rinkinys:
  - originalas jau naudoja CIFAR-10, todėl negalima kartoti to paties;
  - RGB 32×32 palieka dėstytojo CNN ir visą 2 dalies 3 kanalų filtrų kodą;
  - mažesnis už CIFAR-10, tinka CPU;
  - atsisiunčiamas be prisijungimo.

Notebook: [`cnn_tf_flowers.ipynb`](cnn_tf_flowers.ipynb) (ląstelės vykdytos, išvestys išsaugotos).

## Kas pakeista kode ir kas palikta

### Palikta identiška (arba beveik)

- Dėstytojo dalių antraštės, SeaGreen žymės, CNN iliustracijos
- Importai: `tensorflow`, `datasets, layers, models`, `matplotlib`, `numpy`
- Normalizavimas `train_images, test_images = train_images / 255.0, test_images / 255.0`
- 100 vaizdų tinklelis
- CNN sluoksnių seka ir dydžiai (32 / 64 / 64 filtrai, 3×3, ReLU, MaxPool 2×2, Dense 64)
- `compile` (Adam, `SparseCategoricalCrossentropy(from_logits=True)`, `accuracy`)
- `plot_model`, `model.summary`
- Visa **PART 2** filtrų / feature map / rankinės konvoliucijos seka (vaizdai vis dar 32×32×3)
- MLP sluoksniai: Flatten → Dense 32 → 64 → 64
- Tikslumo grafikų kodas

### Pakeista, nes to reikalauja nauji duomenys

| Vieta | Originalas | Ši versija |
| --- | --- | --- |
| Rinkinys | CIFAR-10 (HF `uoft-cs/cifar10`) | tf_flowers tarball + PIL 32×32 |
| `class_names` | 10 CIFAR klasių | 5 gėlių klasės |
| Paskutinis `Dense` | `Dense(10)` (CNN ir MLP) | `Dense(5)` |
| CNN epochos | 20 | **8** (CPU) |
| MLP epochos | 15 | **5** (CPU) |
| Komentarai apie ~70 % / ~40 % | CIFAR-10 | palikti kaip nuoroda į originalą; tikri skaičiai žemiau |

Papildomai: trumpi **lietuviški** paaiškinimai kiekviename žingsnyje (užduotis: „suprasti ir paaiškinti“).

## Rezultatai

Notebook įvykdytas iki galo CPU (be GPU), išvestys išsaugotos `cnn_tf_flowers.ipynb`. Imtis: 2936 treniravimo ir 734 testo vaizdai (32×32 RGB). Epochos sumažintos, kaip nurodyta aukščiau.

| Modelis | Epochos (orig. → čia) | Testo tikslumas |
| --- | --- | --- |
| CNN | 20 → 8 | **67.17 %** (`0.6717`) |
| MLP | 15 → 5 | **45.37 %** (`0.4537`) |

Atsitiktinis spėjimas su 5 klasėmis būtų 20 %. CNN aiškiai lenkia perceptroną — tas pats kokybinis skirtumas, kurį dėstytojo Colab rodė su CIFAR-10 (~70 % vs ~40 %). 2 dalyje rankinė `numpy` konvoliucija (filtras + bias + ReLU) sutapo su Keras pirmojo sluoksnio požymių žemėlapiu.
