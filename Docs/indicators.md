# Indicators Catalog

Fórmulas teóricas de 17 indicadores del panel (16 activos + 1 excluido).

## Definitions

| Term | Formula |
| --- | --- |
| **EBIT** | Ingresos − Costo de ventas − Gastos de venta − Gastos administrativos |
| **EBITDA** | Utilidad neta + Participación trabajadores + Impuesto a la renta + Gastos por intereses + Depreciaciones y amortizaciones |
| **Debt** (deuda con costo) | Obligaciones con instituciones financieras + Valores emitidos |

---

## 1. Financial health

### 1.1 Liquidity

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 1 | Current ratio | Activo corriente / Pasivo corriente | Más alto = más holgura para pagar el corto plazo |
| 2 | Quick ratio | (Activo corriente − Inventarios) / Pasivo corriente | Como el anterior, sin inventarios (el activo menos líquido) |
| 3 | Cash ratio | Efectivo / Pasivo corriente | Cuánto del pasivo corriente cubre el efectivo |

### 1.2 Leverage

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 4 | Debt-to-equity | Pasivo total / Patrimonio | Más alto = más apalancada |
| 5 | Debt ratio | Pasivo total / Activo total | Parte del activo financiada con deuda de terceros |
| 6 | Equity ratio | Patrimonio / Activo total | Autonomía financiera. #5 + #6 = 1 |

### 1.3 Profitability

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 7 | ROE | Utilidad neta / Patrimonio | Ganancia por dólar de patrimonio |
| 8 | ROA | Utilidad neta / Activo total | Ganancia por dólar de activos |
| 9 | Net margin | Utilidad neta / Ingresos | Ganancia por dólar vendido |

---

## 2. Risk

### 2.1 Debt risk

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 10 | Interest coverage | EBIT / Gastos por intereses | Veces que el EBIT cubre los intereses. Más bajo = más riesgo |
| 11 | Cash flow / Debt | Flujo de caja operativo / Deuda total | **Excluded** (requiere el Estado de Flujo de Efectivo) |
| 12 | Debt / EBITDA | Deuda / EBITDA | Años de EBITDA para pagar la deuda. Más alto = más riesgo |

### 2.2 Financial stress

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 13 | Net loss flag | 1 si Utilidad neta < 0; 0 en otro caso | 1 = el año cerró en pérdida |
| 14 | Working capital | Activo corriente − Pasivo corriente | Colchón de corto plazo en dólares |
| 15 | EBIT margin | EBIT / Ingresos | Ganancia operativa por dólar vendido |

### 2.3 Equity risk

| # | Indicator | Formula | How to read it |
| --- | --- | --- | --- |
| 16 | Negative equity flag | 1 si Patrimonio ≤ 0; 0 en otro caso | 1 = patrimonio nulo o negativo |
| 17 | Equity growth | (Patrimonioₜ − Patrimonioₜ₋₁) / Patrimonioₜ₋₁ | Variación anual del patrimonio |