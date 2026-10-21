# 1.4 Gėlių klasifikacija — TensorFlow CNN

VILNIUS TECH kurso *Gilusis mokymas* užduotis 1.4: suprasti dėstytojo Colab užrašus ir perdaryti juos su **savo** vaizdų duomenimis.

| Užrašas | Failas | Originalas |
| --- | --- | --- |
| CNN + filtrai + MLP | [`cnn_tf_flowers.ipynb`](cnn_tf_flowers.ipynb) | [Colab CNN](https://colab.research.google.com/drive/1wx-OBEcjPhAfv8AZ5Fl59mp7RY5Hm0Ql) |

## Kas replikuota

Dėstytojo užrašai **Colab CNN** (`cnn.ipynb`, Algirdas Laukaitis).

- Colab: <https://colab.research.google.com/drive/1wx-OBEcjPhAfv8AZ5Fl59mp7RY5Hm0Ql>
- Originalo duomenys: **CIFAR-10** (32×32 RGB, 10 klasių). Keras `datasets.cifar10.load_data()` ląstelė originale praleista (atsisiuntimas buvęs lėtas); vietoj to naudotas Hugging Face `load_dataset("uoft-cs/cifar10")`.

Langeliai ir skyriai eina ta pačia tvarka: vaizdų įkėlimas → normalizavimas `/255` → pirmų 100 nuotraukų tinklelis → CNN (`Conv2D 32 → Pool → Conv2D 64 → Pool → Conv2D 64 → Flatten → Dense 64 → Dense 10`) → `adam` + `SparseCategoricalCrossentropy(from_logits=True)` → mokymas → tikslumo grafikas → 2 dalis (filtrai, požymių žemėlapiai, rankinė `numpy` konvoliucija) → 3 dalis (MLP palyginimas).

## Duomenų rinkinys ir šaltinis

Naudojamas **tf_flowers** (`flower_photos`): 5 gėlių rūšys, RGB JPEG nuotraukos. Vaizdai sumažinami iki **32×32**, kad dėstytojo CNN ir 2 dalies trijų kanalų filtrų kodas liktų nepakeisti.

| | |
| --- | --- |
| Klasės | `daisy`, `dandelion`, `roses`, `sunflowers`, `tulips` |
| Apimtis | ~3670 JPEG; čia 2936 mokymo + 734 testo (80/20, `seed=42`) |
| Oficialus šaltinis | [TensorFlow `flower_photos.tgz`](https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz) |
| Atsisiuntimas be Kaggle | tas pats Google Storage URL (be prisijungimo) |

Užrašai atsisiunčia archyvą per `tf.keras.utils.get_file`, randa klasės aplankus ir sudaro tuos pačius `numpy` masyvus kaip originalas (`train_images`, `train_labels`, `test_images`, `test_labels`).

## CIFAR-10 → tf_flowers atitikimas

| Originalas (CIFAR-10) | Ši versija (tf_flowers) | Pastaba |
| --- | --- | --- |
| 10 klasių (airplane … truck) | 5 klasės (daisy … tulips) | Kita sritis, kad nebūtų kartojamas CIFAR-10 |
| 32×32 RGB | 32×32 RGB (sumažinta iš JPEG) | CNN `input_shape=(32, 32, 3)` ir PART 2 filtrai lieka |
| `Dense(10)` | `Dense(5)` | Išėjimas pagal klasių skaičių |
| CNN 20 epochų | CNN **8** epochos | CPU |
| MLP 15 epochų | MLP **5** epochos | CPU |
| HF `uoft-cs/cifar10` | `flower_photos.tgz` + PIL | Viešas TensorFlow archyvas |

Palikta identiška: normalizavimas `/255`, 100 vaizdų tinklelis, conv/pool dydžiai, Adam + sparse CE iš logitų, visa 2 dalies filtrų seka, MLP sluoksniai Flatten → Dense 32 → 64 → 64.

## Rezultatai

Užrašai įvykdyti CPU (be GPU), išvestys išsaugotos [`cnn_tf_flowers.ipynb`](cnn_tf_flowers.ipynb). Atsitiktinis spėjimas su 5 klasėmis būtų 20 %.

| Modelis | Epochos (orig. → čia) | Testo tikslumas |
| --- | --- | --- |
| CNN | 20 → 8 | **0.6717** (67,17 %) |
| MLP | 15 → 5 | **0.4537** (45,37 %) |

CNN aiškiai lenkia perceptroną — tas pats kokybinis skirtumas, kurį dėstytojo Colab rodė su CIFAR-10 (~70 % vs ~40 %). 2 dalyje rankinė `numpy` konvoliucija (filtras + bias + ReLU) sutapo su Keras pirmojo sluoksnio požymių žemėlapiu.

## Kaip paleisti

Python 3 su `tensorflow`, `matplotlib`, `pillow`. Iš šio katalogo:

```bash
jupyter notebook cnn_tf_flowers.ipynb
```

arba Colab: atidaryti užrašą ir *Runtime → Run all*. Archyvas atsisiunčiamas be Kaggle paskyros.
