# Methodology — Financial Indicators Panel (Ecuador 2021–2025)

> **Version:** 0.1.0 (first draft) · **Updated:** 2026-10-22

## Table of Contents

1. [Overview](#1-overview)
2. [Glossary](#2-glossary)
3. [Data Sources](#3-data-sources)
4. [How Homologation Works](#4-how-homologation-works)
5. [Building Blocks](#5-building-blocks)
6. [Indicator Framework](#6-indicator-framework)
7. [NA Handling](#7-na-handling)
8. [Pipeline Rules](#8-pipeline-rules)
9. [Known Limitations](#9-known-limitations)
10. [References](#10-references)

---

## 1. Overview

| Item | Value |
| --- | --- |
| Unit of analysis | Empresa–año (*firm-year*), identificada por `RUC` + `AÑO` |
| Period | 2021–2025 |
| Indicators | 17 definidos: **16 activos** + 1 excluido |
| Grouping dimensions | Sector (`CIIU`), año, tamaño |
| Out of scope | Flujo de Caja / Deuda Total (ver [Known Limitations](#9-known-limitations)) |

**El problema que resuelve:** las empresas reportan sus estados financieros en dos catálogos distintos
(contable y tributario), con códigos diferentes para el mismo concepto. Para calcular, por ejemplo, el
ROE de forma consistente hay que decidir de qué cuenta sale cada dato en *ambos* catálogos. Ese
trabajo se llama **homologación** (*account harmonization*) y es el núcleo de este proyecto.

---

## 2. Glossary

| Term | Meaning |
| --- | --- |
| **Supercias** | Superintendencia de Compañías, Valores y Seguros: el regulador que publica los estados financieros |
| **SRI** | Servicio de Rentas Internas: la autoridad tributaria de Ecuador |
| **NIIF** | Normas Internacionales de Información Financiera (*IFRS*): el estándar contable |
| **F101** | Formulario 101 del SRI: declaración del impuesto a la renta de sociedades |
| **Casillero** | Número de campo (*box*) del F101, por ejemplo `361` = Total Activo Corriente |
| **`CUENTA_<code>`** | Columna del catálogo NIIF, por ejemplo `CUENTA_101` = Activo Corriente |
| **RUC** | Registro Único de Contribuyentes: identificador de la empresa |
| **CIIU** | Clasificación industrial (sector de actividad) |
| **CP / LP** | Corto plazo / largo plazo (*current / non-current*) |
| **Homologation** | Definir una sola vez de qué cuenta NIIF y de qué casillero F101 sale cada concepto |
| **NA** | *Not available*: valor que no se puede calcular de forma válida |

---

## 3. Data Sources

### 3.1 NIIF catalog (Supercias)

Estados financieros bajo el estándar contable. Las cuentas llegan como columnas `CUENTA_<code>`
(ej. `CUENTA_101` = Activo Corriente). Es la **fuente primaria** del panel.

### 3.2 Form 101 (SRI)

Declaración tributaria. Sus valores están en casilleros numerados (ej. `361` = Total Activo
Corriente). Responde a una lógica **tributaria**, no contable, así que no todos los casilleros tienen
un equivalente exacto en NIIF.

### 3.3 Why two sources

Cada empresa reporta por **un solo canal**: algunas declaran por NIIF y otras por F101. Por eso el
panel necesita ambas fuentes, y por eso cada concepto se homologa una sola vez para que los dos
grupos de empresas sean comparables.

| Year | Available files | Used in the panel |
| --- | --- | --- |
| 2021–2022 | NIIF · F101 · a third form | NIIF + F101 |
| 2023 | NIIF · F101 | NIIF + F101 |
| 2024–2025 | NIIF only | NIIF |

El proceso se ha ido estandarizando hacia NIIF, por eso los dos últimos años solo traen ese formulario.
El tercer formulario contiene una sola empresa (2021–2022) y se excluye a propósito: homologar un
catálogo completo para rescatar una empresa no compensa (ver [Known Limitations](#9-known-limitations)).

### 3.4 Source rules

- **Cada empresa-año viene de exactamente una fuente** (`NIIF` o `F101`); no hay empresas en ambas.
- El panel guarda una columna `source` por empresa-año, no por indicador.
- **Las dos fuentes son fuentes propias, no respaldo una de la otra.** Como no hay solapamiento,
  tampoco existe validación cruzada entre ellas.
- **Principio de comparabilidad:** la definición del lado F101 debe medir **lo mismo** que la del lado
  NIIF. Si no, una diferencia de método parecería una diferencia entre empresas.
- La unicidad de `RUC` + `AÑO` entre todas las fuentes se verifica en el pipeline (regla R8).
- Si un año futuro trajera una empresa en ambas fuentes, gana NIIF.

### 3.5 Where the data lives

Azure Data Lake (ADLS Gen2) en zonas `raw/ → interim/ → processed/ → panel/`. Detalle en
[`Data/azure-architecture.md`](../Data/azure-architecture.md).

---

## 4. How Homologation Works

### 4.1 Account hierarchy

Los códigos NIIF son jerárquicos: cada nivel agrega a los de abajo.

| Level | Example | Meaning |
| --- | --- | --- |
| 1 | `1` | Activo Total |
| 2 | `101` | Activo Corriente |
| 3 | `10103` | Inventarios |
| 4 | `1010301` | Inventario de materia prima |

**Regla clave:** un código agregado **ya incluye** a sus subcuentas. Si se usa `CUENTA_10103`, no se
suman además `1010301 … 1010313`, porque se contaría dos veces el mismo dinero (*double counting*).

### 4.2 Mapping types (NIIF ↔ F101)

| Type | Meaning | Example |
| --- | --- | --- |
| **Direct** | Una cuenta = un casillero | `CUENTA_1` (Activo Total) ↔ `499` |
| **Aggregated** | Una cuenta = varios casilleros sumados o restados | `CUENTA_10103` (Inventarios) ↔ `339+340+341+342+343+344+345+346 − 347` |
| **Shared** | Un casillero cubre varias subcuentas NIIF | `342` ↔ `1010305` (producido) y `1010306` (comprado) |
| **Joint** | El F101 no separa dos cuentas NIIF | `CUENTA_50201 + CUENTA_50202` (venta + administrativos) ↔ `1030` |
| **Derived** | No existe en NIIF; se calcula | `CUENTA_4` (Total Ingresos) = `401 + 403` |

Consecuencias para el pipeline:

- Un casillero **shared** se asigna al agregado de nivel superior; nunca se duplica en cada subcuenta.
- Una fila **joint** solo existe como suma: con F101 no se puede saber cuánto es venta y cuánto
  administración.

### 4.3 Where the full mapping lives

El plan de cuentas completo (≈155 cuentas con su casillero equivalente) está en
[`config/indicators.yaml`](../config/indicators.yaml). Este documento solo explica la lógica.

---

## 5. Building Blocks

Varios indicadores usan los mismos componentes. Se definen **una sola vez** para que todos sean
consistentes.

### 5.1 Net income

| Source | Account |
| --- | --- |
| NIIF | `CUENTA_707` — Ganancia (pérdida) neta del periodo |
| F101 | Casillero `1099` |

**Por qué no el casillero 801:** el `801` es la utilidad **antes** de participación a trabajadores e
impuesto a la renta (equivale a `CUENTA_600`), y nunca es negativo (la pérdida se declara en el
`802`). Usarlo como utilidad neta inflaría el ROE y ocultaría las pérdidas.

### 5.2 EBIT (*Earnings Before Interest and Taxes*)

```
EBIT = Ingresos ordinarios − Costo de ventas − Gastos de venta − Gastos administrativos
         (401)                (501)            (50201)           (50202)
```

**Por qué no se resta toda la cuenta 502:** incluye gastos financieros (`50203`) y otros gastos
(`50204`). El EBIT es, por definición, *antes de intereses*. Si se restan los intereses en el
numerador y luego se divide entre ellos (cobertura), el indicador queda subestimado.

### 5.3 EBITDA (*EBIT + Depreciation & Amortization*)

Se construye por el **método indirecto** (*bottom-up*), desde la utilidad neta:

```
EBITDA = Utilidad neta + Participación trabajadores + Impuesto a la renta
         + Gastos por intereses + Depreciaciones + Amortizaciones
```

Las depreciaciones y amortizaciones se toman del **costo** y del **gasto**, incluida la amortización
de activos por derecho de uso.

### 5.4 Interest-bearing debt

```
Deuda = Obligaciones con instituciones financieras (CP + LP)
      + Valores emitidos (porción corriente + no corriente)
```

**No es el Pasivo Total:** el pasivo incluye proveedores, impuestos y beneficios a empleados, que no
generan intereses. Se incluyen instituciones **relacionadas y no relacionadas**; tomar solo las
relacionadas subestima la deuda de la mayoría de empresas.

**Qué queda fuera (decisión D-010):** crédito mutuo (`527/567`), arrendamientos NIIF 16
(`20102/20201`) y préstamos de accionistas o relacionadas (`20108/20204`). No existen de forma
equivalente en ambas fuentes y, en el caso de los arrendamientos, los casilleros cambian según el año
del formulario. Ver [Known Limitations](#9-known-limitations).

### 5.5 Interest expense

| Source | Account |
| --- | --- |
| NIIF | `CUENTA_5020301` |
| F101 | Casilleros de intereses `7263 … 7296` |

**Por qué no el casillero 1055:** es *Total gastos financieros y otros gastos no operacionales*;
incluye conceptos que no son intereses y sobreestima el denominador.

**Pendiente de validación:** si se suman los casilleros `7302` y `7792` (intereses implícitos y de
arrendamiento). El criterio es copiar lo que contiene `CUENTA_5020301` en el catálogo NIIF.

---

## 6. Indicator Framework

Dos bloques: **financial health** (1.x) y **risk** (2.x). Las fórmulas exactas están en
[`indicators_reference.md`](indicators_reference.md).

### 6.1 Financial health

| Dimension | What it measures | Indicators |
| --- | --- | --- |
| 1.1 Liquidity | Capacidad de pagar deudas de corto plazo | Current ratio · Quick ratio · Cash ratio |
| 1.2 Leverage | Proporción financiada con deuda | Debt-to-equity · Debt ratio · Equity ratio |
| 1.3 Profitability | Ganancia sobre patrimonio, activos y ventas | ROE · ROA · Net margin |

### 6.2 Risk

| Dimension | What it measures | Indicators |
| --- | --- | --- |
| 2.1 Debt risk | Capacidad de atender la deuda con lo que genera | Interest coverage · Debt/EBITDA · ~~Cash flow/Debt~~ (excluded) |
| 2.2 Financial stress | Señales de deterioro operativo | Net loss flag · Working capital · EBIT margin |
| 2.3 Equity risk | Pérdida de capital propio | Negative equity flag · Equity growth |

### 6.3 Indicator types

| Type | Examples | Note |
| --- | --- | --- |
| Ratio | ROE, Current ratio | Requiere regla NA ([sección 7](#7-na-handling)) |
| Amount | Working capital | En USD; un valor negativo es válido |
| Flag | Net loss flag, Negative equity flag | 0/1; sin regla NA |
| Growth | Equity growth | Necesita el año anterior (`t-1`) de la misma empresa |

---

## 7. NA Handling

Un ratio con denominador cero o negativo **no tiene interpretación financiera**. Una empresa con
patrimonio −100 y pérdida −50 daría un ROE de +50 %, aunque está técnicamente quebrada.

1. Se evalúa el denominador **antes** de dividir.
2. Si no cumple la condición, el resultado es `NA`, nunca `0` ni un valor extremo.
3. La condición que generó el NA **no se pierde**: queda en una bandera aparte
   (ej. `negative_equity_flag`).
4. Las banderas y los montos no llevan regla NA: una pérdida o un capital de trabajo negativo son
   datos válidos.
5. En *Equity growth*, si el patrimonio de `t-1` es negativo, el porcentaje no se interpreta de forma
   convencional y se documenta aparte.

---

## 8. Pipeline Rules

| # | Rule | Why |
| --- | --- | --- |
| R1 | Cruzar siempre por **código**, nunca por nombre de cuenta | Los catálogos `.txt` traen tildes dañadas |
| R2 | Validar la **identidad contable** por empresa-año: `Activo = Pasivo + Patrimonio`, con tolerancia `|A − (P+E)| ≤ máx(1 USD, 0.01 % × A)` | Los redondeos de la fuente rompen la igualdad exacta; si la diferencia es mayor, es un error de extracción |
| R3 | Las filas que fallan R2 van a **cuarentena** (*quarantine*); no se eliminan en silencio | Permite revisar cuántas son y por qué |
| R4 | Casilleros compartidos: se asignan al agregado superior | Evita *double counting* |
| R5 | Arrendamientos: `531/571` **o** `593/594` según el año del formulario, nunca ambos | El SRI cambió los casilleros entre versiones |
| R6 | Las cuentas que usan los indicadores deben existir en el plan homologado | Sin ellas no se calcula el indicador con F101 |
| R7 | El código lee `config/indicators.yaml`; no tiene fórmulas *hard-coded* | *Single source of truth* |
| R8 | `RUC` + `AÑO` debe ser único entre NIIF y F101 (*assert* en cada corrida) | Garantiza que ninguna empresa-año se cuente dos veces |

El umbral de R2 es provisional y se ajusta con la distribución real de las diferencias.

---

## 9. Known Limitations

- **Cash flow / Debt — excluded.** Requiere el Estado de Flujo de Efectivo (NIC 7), un estado
  distinto del Balance y del Estado de Resultados, que no está en ninguno de los dos catálogos.
- **F101 no separa algunos conceptos:** gastos de venta vs administrativos (`1030`), mano de obra
  directa vs indirecta, gastos financieros vs otros gastos (`1055`). Con F101 solo se usan como suma.
- **Signo del casillero 347** (deterioro de inventario): falta verificar en los datos si viene
  positivo o negativo antes de restarlo (**P-005**).
- **Equity growth** pierde el primer año de cada empresa (no existe `t-1`) y los años en que la
  empresa no aparece en `t-1`.
- **Tercer formulario excluido:** una sola empresa en 2021–2022 no tiene homologación.
- **Fuente y año están mezclados:** en 2024–2025 todo es NIIF, así que una tendencia por año puede
  confundirse con el cambio de fuente. Conviene comparar los ratios clave por `source`.
- **Arrendamientos (NIIF 16):** el EBITDA suma de vuelta la amortización de activos por derecho de
  uso, pero la deuda no incluye el pasivo por arrendamientos. En empresas con muchos arriendos,
  Debt/EBITDA sale algo más favorable que la realidad.

---

## 10. References

| File | Content |
| --- | --- |
| [`decisions.md`](decisions.md) | Decision log |
| [`config/indicators.yaml`](../config/indicators.yaml) | Contrato de datos: cuentas, building blocks e indicadores |
| [`indicators_reference.md`](indicators_reference.md) | Fórmulas y reglas NA de cada indicador (generado) |
| [`Data/azure-architecture.md`](../Data/azure-architecture.md) | Arquitectura de datos en Azure |