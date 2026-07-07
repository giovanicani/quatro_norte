from pathlib import Path
import os
import warnings

import numpy as np
import pandas as pd

PROJECT_ROOT = Path.cwd()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent

os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
(PROJECT_ROOT / ".cache" / "matplotlib").mkdir(parents=True, exist_ok=True)

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS = PROJECT_ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"
ANALYSIS_START = pd.Timestamp("2020-01-01")
ANALYSIS_END_EXCLUSIVE = pd.Timestamp("2026-01-01")
ANALYSIS_END = pd.Timestamp("2025-12-31")
KM_MIN_MES_ALVO = 500.0
PREVENTIVE_VMRS_CODES = {"PM"}

for path in [DATA_INTERIM, DATA_PROCESSED, FIGURES, TABLES]:
    path.mkdir(parents=True, exist_ok=True)

warnings.filterwarnings("ignore", category=FutureWarning)
pd.set_option("display.max_columns", 80)
pd.set_option("display.width", 140)

FILES = {
    "dim_carretas": DATA_RAW / "dim_carretas_2020-01-01_to_2025-12-31.csv",
    "fato_contratos": DATA_RAW / "fato_contratos_2020-01-01_to_2025-12-31.csv",
    "fato_gps": DATA_RAW / "fato_gps_2020-01-01_to_2025-12-31.csv",
    "fato_readings": DATA_RAW / "fato_readings_2020-01-01_to_2025-12-31.csv",
    "fato_wo": DATA_RAW / "fato_wo_2020-01-01_to_2025-12-31.csv",
    "fato_wo_labour": DATA_RAW / "fato_wo_labour_2020-01-01_to_2025-12-31.csv",
    "fato_wo_parts": DATA_RAW / "fato_wo_parts_2020-01-01_to_2025-12-31.csv",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def read_csv(name: str, **kwargs) -> pd.DataFrame:
    return normalize_columns(pd.read_csv(FILES[name], low_memory=False, **kwargs))

def month_start(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.to_period("M").dt.to_timestamp()

def as_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def mode_or_unknown(series: pd.Series, unknown: str = "SEM_INFORMACAO") -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return unknown
    return values.mode().iloc[0]

# %% -----

base = pd.read_csv(DATA_PROCESSED / "base_mensal_carreta_deflacionada.csv", parse_dates=["ano_mes"], low_memory=False)
target = "custo_manutencao_preventiva_por_km_deflacionado"

model_data = base.replace([np.inf, -np.inf], np.nan).copy()
population_summary = (
    model_data.groupby("tipo_manutencao", dropna=False)
    .agg(
        observacoes=("id_carreta", "count"),
        obs_km_valido=("km_valido_modelagem_flag", "sum"),
        share_zero_preventivo=("custo_preventivo_total_mes", lambda s: float((s == 0).mean())),
    )
    .reset_index()
)
population_summary.to_csv(TABLES / "05_resumo_populacao_modelagem.csv", index=False)

model_data = model_data[
    model_data["tipo_manutencao"].eq("MAINT")
    & model_data["km_valido_modelagem_flag"].eq(1)
    & model_data[target].notna()
].copy()
model_data = model_data[model_data[target] >= 0].copy()
target_cap = model_data[target].quantile(0.995)
model_data = model_data[model_data[target] <= target_cap].copy()
model_data["teve_custo_preventivo"] = (model_data[target] > 0).astype(int)

model_data.shape, model_data["ano_mes"].min(), model_data["ano_mes"].max(), target_cap

# %% -----

numeric_features = [
    "idade_carreta", "km_rodado_mes", "km_rodado_acum", "km_acumulado",
    "custo_acum_manutencao", "custo_preventivo_acum", "n_os_acum", "n_os_preventivas_acum",
    "custo_medio_movel_3m", "custo_preventivo_medio_movel_3m", "intervalo_medio_os",
    "meses_desde_ultima_os", "km_por_mes", "franquia_km_mensal",
    "duracao_contrato_meses", "idade_contrato_meses_no_mes",
]
categorical_features = [
    "cod_montadora", "cod_modelo", "flag_refrigerado", "tipo_contrato",
    "cod_grupo_manutencao", "regiao_operacao",
]
numeric_features = [c for c in numeric_features if c in model_data.columns]
categorical_features = [c for c in categorical_features if c in model_data.columns]

features_removidas = pd.DataFrame([
    {
        "feature": "prop_pecas_garantia",
        "motivo": "quase sem variacao util: a base registra pouquissimas pecas em garantia; mantida apenas como diagnostico",
        "share_meses_modelagem_com_garantia": float(model_data.get("prop_pecas_garantia", pd.Series(dtype=float)).fillna(0).gt(0).mean()),
    }
])
features_removidas.to_csv(TABLES / "05_features_removidas_modelagem.csv", index=False)

test_start = model_data["ano_mes"].max() - pd.DateOffset(months=11)
train = model_data[model_data["ano_mes"] < test_start].copy()
test = model_data[model_data["ano_mes"] >= test_start].copy()

X_train = train[numeric_features + categorical_features]
y_train = train[target]
X_test = test[numeric_features + categorical_features]
y_test = test[target]

split_summary = pd.DataFrame([
    {"particao": "treino", "linhas": len(train), "inicio": train["ano_mes"].min(), "fim": train["ano_mes"].max(), "share_zero_preventivo": float((train[target] == 0).mean())},
    {"particao": "teste", "linhas": len(test), "inicio": test["ano_mes"].min(), "fim": test["ano_mes"].max(), "share_zero_preventivo": float((test[target] == 0).mean())},
])
split_summary.to_csv(TABLES / "05_particao_temporal.csv", index=False)
split_summary

# %% -----

from sklearn.compose import ColumnTransformer
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge, SGDClassifier
from sklearn.compose import TransformedTargetRegressor
from sklearn.inspection import permutation_importance

numeric_scaled = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
numeric_plain = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
])
categorical_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=100, sparse_output=True)),
])

preprocess_scaled = ColumnTransformer([
    ("num", numeric_scaled, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])
preprocess_plain = ColumnTransformer([
    ("num", numeric_plain, numeric_features),
    ("cat", categorical_pipe, categorical_features),
])

simple_feature = ["km_rodado_mes"] if "km_rodado_mes" in numeric_features else numeric_features[:1]
preprocess_simple = ColumnTransformer([
    ("num", numeric_scaled, simple_feature),
])

models = {
    "regressao_linear_simples": Pipeline([("prep", preprocess_simple), ("model", LinearRegression())]),
    "regressao_linear_multipla": Pipeline([("prep", preprocess_scaled), ("model", LinearRegression())]),
    "ridge_multipla": Pipeline([("prep", preprocess_scaled), ("model", Ridge(alpha=10.0))]),
    "ridge_log1p": TransformedTargetRegressor(
        regressor=Pipeline([("prep", preprocess_scaled), ("model", Ridge(alpha=10.0))]),
        func=np.log1p,
        inverse_func=np.expm1,
    ),
    "regressao_polinomial_grau_2": Pipeline([
        ("prep", ColumnTransformer([("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("scaler", StandardScaler()),
        ]), numeric_features[:6])])),
        ("model", LinearRegression()),
    ]),
    "arvore_decisao": Pipeline([("prep", preprocess_plain), ("model", DecisionTreeRegressor(max_depth=8, min_samples_leaf=50, random_state=42))]),
    "random_forest": Pipeline([("prep", preprocess_plain), ("model", RandomForestRegressor(n_estimators=30, min_samples_leaf=40, random_state=42, n_jobs=-1))]),
    "gradient_boosting": Pipeline([("prep", preprocess_plain), ("model", GradientBoostingRegressor(random_state=42, max_depth=3, n_estimators=70))]),
    "knn": Pipeline([("prep", preprocess_scaled), ("model", KNeighborsRegressor(n_neighbors=25, weights="distance"))]),
}

MAX_TREE_TRAIN_ROWS = 80000
MAX_KNN_TRAIN_ROWS = 30000
MAX_KNN_TEST_ROWS = 10000
SAMPLED_TRAINING_MODELS = {"arvore_decisao", "random_forest", "gradient_boosting"}
metrics = []
predictions = {}
for name, pipeline in models.items():
    if name == "knn":
        train_eval = train.sample(n=min(MAX_KNN_TRAIN_ROWS, len(train)), random_state=42)
        test_eval_sample = test.sample(n=min(MAX_KNN_TEST_ROWS, len(test)), random_state=42)
        x_train_fit = train_eval[numeric_features + categorical_features]
        y_train_fit = train_eval[target]
        x_test_eval = test_eval_sample[numeric_features + categorical_features]
        y_test_eval = test_eval_sample[target]
        avaliacao = "amostra_teste_temporal"
    elif name in SAMPLED_TRAINING_MODELS:
        train_eval = train.sample(n=min(MAX_TREE_TRAIN_ROWS, len(train)), random_state=42)
        x_train_fit = train_eval[numeric_features + categorical_features]
        y_train_fit = train_eval[target]
        x_test_eval = X_test
        y_test_eval = y_test
        avaliacao = "teste_temporal_completo"
    else:
        x_train_fit = X_train
        y_train_fit = y_train
        x_test_eval = X_test
        y_test_eval = y_test
        avaliacao = "teste_temporal_completo"
    pipeline.fit(x_train_fit, y_train_fit)
    pred = pipeline.predict(x_test_eval)
    if avaliacao == "teste_temporal_completo":
        predictions[name] = pred
    rmse = mean_squared_error(y_test_eval, pred) ** 0.5
    metrics.append({
        "modelo": name,
        "avaliacao": avaliacao,
        "elegivel_recomendacao": avaliacao == "teste_temporal_completo",
        "r2": r2_score(y_test_eval, pred),
        "rmse": rmse,
        "mae": mean_absolute_error(y_test_eval, pred),
    })

metrics = pd.DataFrame(metrics).sort_values("rmse")
metrics.to_csv(TABLES / "05_metricas_modelos.csv", index=False)
best_model_name = metrics.loc[metrics["elegivel_recomendacao"]].sort_values("rmse").iloc[0]["modelo"]
best_model = models[best_model_name] if best_model_name in models else None
best_model_is_direct_pipeline = best_model is not None
metrics

# %% -----

binary_target = "teve_custo_preventivo"
MAX_HURDLE_CLASSIFIER_ROWS = 120000
MAX_HURDLE_POSITIVE_ROWS = 60000

hurdle_classifier = Pipeline([
    ("prep", preprocess_scaled),
    ("model", SGDClassifier(
        loss="log_loss",
        class_weight="balanced",
        random_state=42,
        max_iter=1000,
        tol=1e-3,
    )),
])

classifier_train = train.sample(n=min(MAX_HURDLE_CLASSIFIER_ROWS, len(train)), random_state=42)
hurdle_classifier.fit(classifier_train[numeric_features + categorical_features], classifier_train[binary_target])
prob_positive = hurdle_classifier.predict_proba(X_test)[:, 1]
class_pred = (prob_positive >= 0.5).astype(int)
y_test_binary = test[binary_target].to_numpy()

classification_metrics = pd.DataFrame([{
    "modelo": "hurdle_sgd_classifier",
    "roc_auc": roc_auc_score(y_test_binary, prob_positive) if len(np.unique(y_test_binary)) > 1 else np.nan,
    "average_precision": average_precision_score(y_test_binary, prob_positive) if len(np.unique(y_test_binary)) > 1 else np.nan,
    "brier_score": brier_score_loss(y_test_binary, prob_positive),
    "precision_threshold_0_5": precision_score(y_test_binary, class_pred, zero_division=0),
    "recall_threshold_0_5": recall_score(y_test_binary, class_pred, zero_division=0),
    "f1_threshold_0_5": f1_score(y_test_binary, class_pred, zero_division=0),
    "share_positivo_teste": float(y_test_binary.mean()),
    "share_positivo_predito_0_5": float(class_pred.mean()),
}])

positive_train = train[train[target] > 0].copy()
positive_train_fit = positive_train.sample(n=min(MAX_HURDLE_POSITIVE_ROWS, len(positive_train)), random_state=42)
hurdle_positive_regressor = TransformedTargetRegressor(
    regressor=Pipeline([
        ("prep", preprocess_plain),
        ("model", GradientBoostingRegressor(random_state=42, max_depth=3, n_estimators=70)),
    ]),
    func=np.log1p,
    inverse_func=np.expm1,
)
hurdle_positive_regressor.fit(positive_train_fit[numeric_features + categorical_features], positive_train_fit[target])
positive_magnitude_pred = np.maximum(hurdle_positive_regressor.predict(X_test), 0)
hurdle_pred = prob_positive * positive_magnitude_pred

hurdle_row = {
    "modelo": "hurdle_sgd_gb",
    "avaliacao": "teste_temporal_completo",
    "elegivel_recomendacao": True,
    "r2": r2_score(y_test, hurdle_pred),
    "rmse": mean_squared_error(y_test, hurdle_pred) ** 0.5,
    "mae": mean_absolute_error(y_test, hurdle_pred),
}

predictions["hurdle_sgd_gb"] = hurdle_pred
metrics = (
    pd.concat([metrics, pd.DataFrame([hurdle_row])], ignore_index=True)
    .drop_duplicates(subset=["modelo"], keep="last")
    .sort_values("rmse")
)
metrics.to_csv(TABLES / "05_metricas_modelos.csv", index=False)
classification_metrics.to_csv(TABLES / "05_hurdle_classificacao.csv", index=False)
pd.DataFrame([hurdle_row]).to_csv(TABLES / "05_hurdle_metricas.csv", index=False)

best_model_name = metrics.loc[metrics["elegivel_recomendacao"]].sort_values("rmse").iloc[0]["modelo"]
best_model = models[best_model_name] if best_model_name in models else None
best_model_is_direct_pipeline = best_model is not None

pd.concat([
    classification_metrics,
    pd.DataFrame([{
        "modelo": "hurdle_sgd_gb",
        "roc_auc": np.nan,
        "average_precision": np.nan,
        "brier_score": np.nan,
        "precision_threshold_0_5": np.nan,
        "recall_threshold_0_5": np.nan,
        "f1_threshold_0_5": np.nan,
        "share_positivo_teste": float(y_test_binary.mean()),
        "share_positivo_predito_0_5": float(class_pred.mean()),
        "rmse_esperado": hurdle_row["rmse"],
        "mae_esperado": hurdle_row["mae"],
        "r2_esperado": hurdle_row["r2"],
    }])
], ignore_index=True)

# %% -----

mirror_target = "custo_preventivo_mao_obra_por_km_deflacionado"
mirror_rows = []

if mirror_target in model_data.columns:
    mirror_data = model_data[
        model_data[mirror_target].notna()
        & (model_data[mirror_target] >= 0)
    ].copy()
    mirror_cap = mirror_data[mirror_target].quantile(0.995)
    mirror_data = mirror_data[mirror_data[mirror_target] <= mirror_cap].copy()
    mirror_train = mirror_data[mirror_data["ano_mes"] < test_start].copy()
    mirror_test = mirror_data[mirror_data["ano_mes"] >= test_start].copy()

    mirror_train_fit = mirror_train.sample(n=min(MAX_TREE_TRAIN_ROWS, len(mirror_train)), random_state=42)
    mirror_model = clone(models["random_forest"])
    mirror_model.fit(
        mirror_train_fit[numeric_features + categorical_features],
        mirror_train_fit[mirror_target],
    )
    mirror_pred = mirror_model.predict(mirror_test[numeric_features + categorical_features])

    total_rf = metrics.loc[metrics["modelo"].eq("random_forest")].iloc[0]
    mirror_rows = [
        {
            "alvo": target,
            "descricao": "custo preventivo total por km: mao de obra preventiva + pecas de OS com linha preventiva",
            "modelo": "random_forest",
            "observacoes_teste": len(test),
            "share_zero_teste": float((test[target] == 0).mean()),
            "r2": total_rf["r2"],
            "rmse": total_rf["rmse"],
            "mae": total_rf["mae"],
        },
        {
            "alvo": mirror_target,
            "descricao": "alvo-espelho mais limpo: apenas mao de obra preventiva atribuivel por linha VMRS",
            "modelo": "random_forest",
            "observacoes_teste": len(mirror_test),
            "share_zero_teste": float((mirror_test[mirror_target] == 0).mean()),
            "r2": r2_score(mirror_test[mirror_target], mirror_pred),
            "rmse": mean_squared_error(mirror_test[mirror_target], mirror_pred) ** 0.5,
            "mae": mean_absolute_error(mirror_test[mirror_target], mirror_pred),
        },
    ]

alvo_espelho = pd.DataFrame(mirror_rows)
if len(alvo_espelho):
    alvo_espelho["delta_r2_vs_total"] = alvo_espelho["r2"] - alvo_espelho.loc[0, "r2"]
    alvo_espelho["delta_rmse_vs_total"] = alvo_espelho["rmse"] - alvo_espelho.loc[0, "rmse"]
alvo_espelho.to_csv(TABLES / "05_alvo_espelho_mao_obra.csv", index=False)
alvo_espelho

# %% -----

def temporal_folds(data: pd.DataFrame, min_train_months: int = 24, validation_months: int = 6, n_folds: int = 3):
    months = sorted(data["ano_mes"].dropna().unique())
    folds = []
    latest_validation_end = len(months) - 12
    candidate_ends = np.linspace(min_train_months, max(min_train_months + 1, latest_validation_end - validation_months), n_folds, dtype=int)
    for train_end in sorted(set(candidate_ends)):
        val_start = train_end
        val_end = min(train_end + validation_months, len(months))
        if val_end <= val_start or val_end > latest_validation_end:
            continue
        folds.append((months[:train_end], months[val_start:val_end]))
    return folds

cv_models = {name: models[name] for name in ["ridge_log1p", "arvore_decisao", "gradient_boosting"] if name in models}
cv_rows = []
for fold_idx, (train_months, val_months) in enumerate(temporal_folds(model_data), start=1):
    fold_train = model_data[model_data["ano_mes"].isin(train_months)]
    fold_val = model_data[model_data["ano_mes"].isin(val_months)]
    if len(fold_train) == 0 or len(fold_val) == 0:
        continue
    for name, pipeline in cv_models.items():
        fold_train_fit = fold_train.sample(n=min(50000, len(fold_train)), random_state=42) if name in SAMPLED_TRAINING_MODELS else fold_train
        fold_pipeline = clone(pipeline)
        fold_pipeline.fit(fold_train_fit[numeric_features + categorical_features], fold_train_fit[target])
        pred = fold_pipeline.predict(fold_val[numeric_features + categorical_features])
        cv_rows.append({
            "fold": fold_idx,
            "modelo": name,
            "treino_inicio": min(train_months),
            "treino_fim": max(train_months),
            "validacao_inicio": min(val_months),
            "validacao_fim": max(val_months),
            "r2": r2_score(fold_val[target], pred),
            "rmse": mean_squared_error(fold_val[target], pred) ** 0.5,
            "mae": mean_absolute_error(fold_val[target], pred),
        })

cv_metrics = pd.DataFrame(cv_rows)
cv_metrics.to_csv(TABLES / "05_validacao_temporal_expansiva.csv", index=False)
cv_metrics.groupby("modelo", as_index=False).agg(rmse_medio=("rmse", "mean"), mae_medio=("mae", "mean"), r2_medio=("r2", "mean")).sort_values("rmse_medio")

# %% -----

from sklearn.linear_model import LinearRegression as SkLinearRegression

vif_data = model_data[numeric_features].copy()
vif_sample = vif_data.sample(n=min(50000, len(vif_data)), random_state=42) if len(vif_data) else vif_data
vif_sample = pd.DataFrame(
    SimpleImputer(strategy="median").fit_transform(vif_sample),
    columns=numeric_features,
)

vif_rows = []
for feature in numeric_features:
    other_features = [c for c in numeric_features if c != feature]
    if not other_features:
        continue
    y_feature = vif_sample[feature]
    x_other = vif_sample[other_features]
    r2_feature = SkLinearRegression().fit(x_other, y_feature).score(x_other, y_feature)
    vif_rows.append({
        "feature": feature,
        "r2_explicado_pelas_demais": r2_feature,
        "vif_aproximado": np.inf if r2_feature >= 0.999999 else 1 / (1 - r2_feature),
    })

vif = pd.DataFrame(vif_rows).sort_values("vif_aproximado", ascending=False)
vif.to_csv(TABLES / "05_vif_features_numericas.csv", index=False)
vif.head(15)

# %% -----

rf = models["random_forest"]
rf_model = rf.named_steps["model"]
prep = rf.named_steps["prep"]

try:
    feature_names = prep.get_feature_names_out()
except Exception:
    feature_names = [f"feature_{i}" for i in range(len(rf_model.feature_importances_))]

importance = (
    pd.DataFrame({"feature": feature_names, "importancia": rf_model.feature_importances_})
    .sort_values("importancia", ascending=False)
)
importance.to_csv(TABLES / "05_importancia_variaveis_random_forest.csv", index=False)
perm_sample = test.sample(n=min(12000, len(test)), random_state=42)
perm = permutation_importance(
    rf,
    perm_sample[numeric_features + categorical_features],
    perm_sample[target],
    n_repeats=5,
    random_state=42,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
)
permutation_df = (
    pd.DataFrame({
        "feature": numeric_features + categorical_features,
        "importancia_permutacao_mae": perm.importances_mean,
        "importancia_permutacao_std": perm.importances_std,
    })
    .sort_values("importancia_permutacao_mae", ascending=False)
)
permutation_df.to_csv(TABLES / "05_importancia_permutacao_random_forest.csv", index=False)
importance.head(20)

# %% -----

test_eval = test[["id_carreta", "ano_mes", "cod_montadora", "tipo_contrato", "regiao_operacao", "idade_carreta", target]].copy()
test_eval["predito"] = predictions[best_model_name]
test_eval["erro"] = test_eval["predito"] - test_eval[target]
test_eval["erro_abs"] = test_eval["erro"].abs()
test_eval["faixa_idade"] = pd.cut(test_eval["idade_carreta"], bins=[0, 3, 6, 10, 20, np.inf], include_lowest=True)

error_by_segment = []
for col in ["cod_montadora", "tipo_contrato", "regiao_operacao", "faixa_idade"]:
    if col in test_eval.columns:
        seg = (
            test_eval.groupby(col, dropna=False)
            .agg(observacoes=("erro_abs", "count"), mae=("erro_abs", "mean"), vies=("erro", "mean"))
            .reset_index()
        )
        seg["segmento"] = col
        seg = seg.rename(columns={col: "valor_segmento"})
        error_by_segment.append(seg)

error_by_segment = pd.concat(error_by_segment, ignore_index=True)
error_by_segment.to_csv(TABLES / "05_erro_por_segmento.csv", index=False)

best_row = metrics.loc[metrics["modelo"].eq(best_model_name)].iloc[0]
recommendation = pd.DataFrame([{
    "modelo_recomendado": best_model_name,
    "criterio": "menor RMSE no conjunto de teste temporal da populacao MAINT",
    "alvo": target,
    "populacao": "tipo_manutencao = MAINT; km_rodado_mes >= piso metodologico",
    "pipeline_direto_disponivel": best_model_is_direct_pipeline,
    "rmse": best_row["rmse"],
    "mae": best_row["mae"],
    "r2": best_row["r2"],
}])
recommendation.to_csv(TABLES / "05_modelo_recomendado.csv", index=False)

recommendation