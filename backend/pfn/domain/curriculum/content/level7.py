"""LEVEL 7 - Machine learning foundations."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l7.ml_fundamentals",
        level=7,
        order_index=1,
        domain="machine_learning",
        title_ar="أساسيات التعلّم الآلي",
        title_en="Machine learning fundamentals",
        summary_ar="تقسيم البيانات، التوحيد، الانحدار الخطي، ومقاييس الخطأ.",
        summary_en="Splitting data, scaling, linear regression and error metrics.",
        explanation_ar="""أي تجربة تعلّم آلي تبدأ بنفس الانقسام:

1. **تقسيم البيانات** قبل أي شيء: تدريب (train) واختبار (test). لا تلمس الاختبار
   حتى تنتهي من النمذجة — وإلا فأنت تقيس حفظاً لا تعميماً.
2. **التوحيد (standardization)**: `z = (x - mean) / std`. احسب المتوسط والانحراف
   من **بيانات التدريب فقط** ثم طبّقهما على الاختبار (تسرّب البيانات خطأ شائع).
3. **النموذج**: الانحدار الخطي يحل `y ≈ Xw + b` بأصغر مجموع مربعات.
   الحل المغلق: `w = (XᵀX)⁻¹ Xᵀy` (أضف عموداً من الواحدات للثابت `b`).
4. **المقاييس**:
   - `MAE` متوسط القيمة المطلقة للخطأ (بنفس وحدة الهدف)،
   - `RMSE` جذر متوسط مربع الخطأ (يعاقب الأخطاء الكبيرة أكثر)،
   - `R²` نسبة التباين المفسّر: `1` مثالي، `0` يعني أداءً بقدر المتوسط.

قاعدة ذهبية: قارن دائماً أداء التدريب بأداء الاختبار. الفجوة الكبيرة = تعلّم زائد.""",
        explanation_en="""Every machine learning experiment starts with the same split:

1. **Split the data** first: train and test. Do not touch the test set until the modelling is
   finished - otherwise you are measuring memorisation, not generalisation.
2. **Standardisation**: `z = (x - mean) / std`. Compute the mean and standard deviation from
   the **training data only**, then apply them to the test set (leakage is a classic bug).
3. **The model**: linear regression solves `y ~ Xw + b` by minimising squared error.
   The closed form is `w = (X'X)^-1 X'y` (append a column of ones for the intercept `b`).
4. **Metrics**:
   - `MAE` - mean absolute error, in the target's units,
   - `RMSE` - root mean squared error, penalising large mistakes more,
   - `R^2` - the share of variance explained: `1` is perfect, `0` means no better than the mean.

Golden rule: always compare training performance with test performance. A wide gap is
overfitting.""",
        skills=("ml.supervised", "ml.regression", "ml.evaluation"),
        prerequisites=("l5.numpy_foundations", "l6.complexity"),
        example_code="""import numpy as np

rng = np.random.default_rng(0)

# y = 3x + 7 + noise
X = 2 * rng.random((200, 1))
y = 3 * X.ravel() + 7 + rng.normal(0, 0.5, size=200)

order = rng.permutation(len(X))
cut = int(0.8 * len(X))
train, test = order[:cut], order[cut:]

X_train, y_train = X[train], y[train]
X_test, y_test = X[test], y[test]

mean = X_train.mean(axis=0)
std = X_train.std(axis=0)
X_train_s = (X_train - mean) / std
X_test_s = (X_test - mean) / std

# closed form: append a bias column of ones
A = np.hstack([X_train_s, np.ones((len(X_train_s), 1))])
weights = np.linalg.solve(A.T @ A, A.T @ y_train)
print("weights (scaled):", np.round(weights, 3))

B = np.hstack([X_test_s, np.ones((len(X_test_s), 1))])
predictions = B @ weights
rmse = float(np.sqrt(((predictions - y_test) ** 2).mean()))
print("test RMSE:", round(rmse, 3))
print("baseline (predict the mean):", round(float(np.sqrt(((y_train.mean() - y_test) ** 2).mean())), 3))
""",
        example_notes_ar="التوحيد حُسب من بيانات التدريب وطُبّق على الاختبار — هذه هي القاعدة الصحيحة.",
        example_notes_en="Scaling was fitted on the training data and applied to the test data - that is the correct order.",
        experiment_code="""import numpy as np

rng = np.random.default_rng(1)
X = rng.normal(size=(300, 1))
y = 2 * X.ravel() + 1 + rng.normal(0, 0.3, size=300)

A = np.hstack([X, np.ones((len(X), 1))])


def loss(weights):
    residuals = A @ weights - y
    return float((residuals ** 2).mean())


weights = np.zeros(2)
learning_rate = 0.1
for step in range(1, 61):
    gradient = 2 * A.T @ (A @ weights - y) / len(X)
    weights -= learning_rate * gradient
    if step in (1, 5, 20, 60):
        print(f"step {step:>3}: loss {loss(weights):8.4f}  weights {np.round(weights, 3)}")

closed = np.linalg.solve(A.T @ A, A.T @ y)
print("closed form weights:", np.round(closed, 3))
print("gradient descent   :", np.round(weights, 3))
""",
        experiment_brief_ar="غيّر `learning_rate` إلى 2.0 وشاهد انفجار الخسارة، ثم إلى 0.001 وشاهد البطء.",
        experiment_brief_en="Change `learning_rate` to 2.0 and watch the loss explode, then to 0.001 and watch it crawl.",
        task=TaskSpec(
            brief_ar="""اكتب (بـ numpy فقط):
1. `train_test_split(X, y, test_size=0.2, seed=0)` تُعيد `(X_train, X_test, y_train, y_test)`
   بتقسيم عشوائي محدّد بالبذرة.
2. `standardize(X)` تُعيد `(scaled, mean, std)` مع حماية من القسمة على صفر.
3. `fit_linear(X, y)` تُعيد مصفوفة أوزان تحتوي الثابت (أضف عموداً من الواحدات).
4. `predict_linear(X, weights)` و`rmse(y_true, y_pred)` و`r2_score(y_true, y_pred)`.""",
            brief_en="""Write (numpy only):
1. `train_test_split(X, y, test_size=0.2, seed=0)` returning `(X_train, X_test, y_train, y_test)`
   with a seeded random split.
2. `standardize(X)` returning `(scaled, mean, std)`, guarding against division by zero.
3. `fit_linear(X, y)` returning a weight vector including the intercept (append a ones column).
4. `predict_linear(X, weights)`, `rmse(y_true, y_pred)` and `r2_score(y_true, y_pred)`.""",
            starter_code="""import numpy as np


def train_test_split(X, y, test_size=0.2, seed=0):
    pass


def standardize(X):
    pass


def fit_linear(X, y):
    pass


def predict_linear(X, weights):
    pass


def rmse(y_true, y_pred):
    pass


def r2_score(y_true, y_pred):
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import train_test_split, fit_linear, predict_linear

def test_fit_recovers_a_line():
    X = np.arange(20, dtype=float).reshape(-1, 1)
    y = 3 * X.ravel() + 7
    weights = fit_linear(X, y)
    assert abs(predict_linear(X, weights)[0] - 7) < 1e-6
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import train_test_split, standardize, fit_linear, predict_linear, rmse, r2_score

def make_data(n=100, seed=3):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 2))
    y = 4 * X[:, 0] - 2 * X[:, 1] + 1
    return X, y

def test_split_sizes():
    X, y = make_data(50)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, seed=7)
    assert len(X_train) == 40 and len(X_test) == 10
    assert len(y_train) == 40 and len(y_test) == 10

def test_split_is_deterministic():
    X, y = make_data(50)
    first = train_test_split(X, y, seed=1)
    second = train_test_split(X, y, seed=1)
    assert np.allclose(first[0], second[0])
    assert np.allclose(first[2], second[2])

def test_split_partitions_all_rows():
    X, y = make_data(50)
    X_train, X_test, _, _ = train_test_split(X, y, seed=2)
    assert len(X_train) + len(X_test) == 50

def test_standardize_stats():
    X = np.array([[1.0], [2.0], [3.0]])
    scaled, mean, std = standardize(X)
    assert abs(mean[0] - 2.0) < 1e-9
    assert abs(float(scaled.mean())) < 1e-9
    assert abs(float(scaled.std()) - 1.0) < 1e-6

def test_standardize_constant_column():
    X = np.array([[5.0], [5.0]])
    scaled, _, _ = standardize(X)
    assert np.all(np.isfinite(scaled))

def test_fit_is_accurate():
    X, y = make_data()
    weights = fit_linear(X, y)
    assert rmse(y, predict_linear(X, weights)) < 1e-6

def test_rmse_and_r2():
    y_true = np.array([1.0, 2.0, 3.0])
    assert rmse(y_true, y_true) == 0.0
    assert abs(r2_score(y_true, y_true) - 1.0) < 1e-9
    assert abs(rmse(y_true, np.array([2.0, 3.0, 4.0])) - 1.0) < 1e-9

def test_r2_worse_than_mean():
    y_true = np.array([1.0, 2.0, 3.0])
    assert r2_score(y_true, np.array([10.0, 20.0, 30.0])) < 0
"""},
            reference_solution="""import numpy as np


def train_test_split(X, y, test_size=0.2, seed=0):
    X = np.asarray(X)
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(X))
    cut = int(round(len(X) * (1 - test_size)))
    train, test = order[:cut], order[cut:]
    return X[train], X[test], y[train], y[test]


def standardize(X):
    data = np.asarray(X, dtype=float)
    mean = data.mean(axis=0)
    std = data.std(axis=0)
    safe = np.where(std == 0, 1.0, std)
    return (data - mean) / safe, mean, safe


def fit_linear(X, y):
    data = np.asarray(X, dtype=float)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    design = np.hstack([data, np.ones((len(data), 1))])
    return np.linalg.solve(design.T @ design, design.T @ np.asarray(y, dtype=float))


def predict_linear(X, weights):
    data = np.asarray(X, dtype=float)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    design = np.hstack([data, np.ones((len(data), 1))])
    return design @ weights


def rmse(y_true, y_pred):
    difference = np.asarray(y_true, dtype=float) - np.asarray(y_pred, dtype=float)
    return float(np.sqrt((difference ** 2).mean()))


def r2_score(y_true, y_pred):
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    residual = ((actual - predicted) ** 2).sum()
    spread = ((actual - actual.mean()) ** 2).sum()
    if spread == 0:
        return 1.0 if residual == 0 else 0.0
    return float(1 - residual / spread)
""",
            hints=(
                "Seed a `default_rng` and permute the indices - never reshuffle X and y separately.",
                "Replace zero standard deviations with 1.0 instead of dividing by zero.",
                "Append a ones column to X so the weight vector carries the intercept.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `GradientDescentRegressor` يدرّب انحداراً خطياً بالنزول التدريجي،
وصنف `PolynomialFeatures`:

- `PolynomialFeatures(degree).fit_transform(X)` تُضيف الأعمدة `x, x², ..., x^d` (والثابت لا يُضاف).
- `GradientDescentRegressor(learning_rate=0.01, epochs=500)` بطرق `fit(X, y)`،
  `predict(X)`، وخاصية `loss_history_` (قائمة تنقص مع التدريب).
- يجب أن يعمل بعد توحيد البيانات، وأن يتعامل مع ميزات متعددة.""",
            brief_en="""Write a `GradientDescentRegressor` training linear regression by gradient descent, and a
`PolynomialFeatures` transformer:

- `PolynomialFeatures(degree).fit_transform(X)` appends the columns `x, x^2, ..., x^d`
  (no constant column).
- `GradientDescentRegressor(learning_rate=0.01, epochs=500)` with `fit(X, y)`, `predict(X)` and
  a `loss_history_` list that decreases while training.
- It must work after scaling and handle multiple features.""",
            independent=True,
            starter_code="""import numpy as np


class PolynomialFeatures:
    def __init__(self, degree=2):
        pass


class GradientDescentRegressor:
    def __init__(self, learning_rate=0.01, epochs=500):
        pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import PolynomialFeatures

def test_polynomial_shape():
    expanded = PolynomialFeatures(degree=3).fit_transform(np.array([[2.0]]))
    assert expanded.shape == (1, 3)
    assert np.allclose(expanded, [[2.0, 4.0, 8.0]])
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import PolynomialFeatures, GradientDescentRegressor

def make_line(n=200, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 1))
    y = 3 * X.ravel() + 2
    return X, y

def test_polynomial_multiple_columns():
    X = np.array([[2.0, 3.0]])
    assert PolynomialFeatures(2).fit_transform(X).shape == (1, 4)

def test_polynomial_degree_one():
    X = np.array([[5.0]])
    assert np.allclose(PolynomialFeatures(1).fit_transform(X), [[5.0]])

def test_regressor_fits_a_line():
    X, y = make_line()
    model = GradientDescentRegressor(learning_rate=0.05, epochs=800).fit(X, y)
    residual = float(np.sqrt(((model.predict(X) - y) ** 2).mean()))
    assert residual < 0.05

def test_loss_history_decreases():
    X, y = make_line()
    model = GradientDescentRegressor(learning_rate=0.05, epochs=200).fit(X, y)
    assert len(model.loss_history_) == 200
    assert model.loss_history_[-1] < model.loss_history_[0]

def test_predict_shape():
    X, y = make_line(30)
    model = GradientDescentRegressor(epochs=50).fit(X, y)
    assert model.predict(X).shape == (30,)

def test_multiple_features():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(100, 3))
    y = X @ np.array([1.0, -2.0, 0.5]) + 1
    mean, std = X.mean(axis=0), X.std(axis=0)
    model = GradientDescentRegressor(learning_rate=0.1, epochs=500).fit((X - mean) / std, y)
    assert float(np.sqrt(((model.predict((X - mean) / std) - y) ** 2).mean())) < 0.1
"""},
            reference_solution="""import numpy as np


class PolynomialFeatures:
    def __init__(self, degree=2):
        self.degree = int(degree)

    def fit(self, X):
        return self

    def fit_transform(self, X):
        data = np.asarray(X, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        columns = [data ** power for power in range(1, self.degree + 1)]
        return np.hstack(columns)


class GradientDescentRegressor:
    def __init__(self, learning_rate=0.01, epochs=500):
        self.learning_rate = float(learning_rate)
        self.epochs = int(epochs)
        self.weights = None
        self.loss_history_ = []

    def fit(self, X, y):
        data = np.asarray(X, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        design = np.hstack([data, np.ones((len(data), 1))])
        target = np.asarray(y, dtype=float)
        self.weights = np.zeros(design.shape[1])
        for _ in range(self.epochs):
            residuals = design @ self.weights - target
            gradient = 2 * design.T @ residuals / len(design)
            self.weights -= self.learning_rate * gradient
            self.loss_history_.append(float((residuals ** 2).mean()))
        return self

    def predict(self, X):
        data = np.asarray(X, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        design = np.hstack([data, np.ones((len(data), 1))])
        return design @ self.weights
""",
        ),
        transfer_ar="استخدم الانحدار في Data Empire لتوقّع الطلب قبل بناء النموذج النهائي.",
        transfer_en="Use regression in Data Empire to forecast demand before the final model.",
        references=(
            ("scikit-learn - linear models", "https://scikit-learn.org/stable/modules/linear_model.html"),
            ("An Introduction to Statistical Learning", "https://www.statlearning.com/"),
        ),
    ),
    CurriculumModule(
        id="l7.classification",
        level=7,
        order_index=2,
        domain="machine_learning",
        title_ar="التصنيف",
        title_en="Classification",
        summary_ar="kNN والانحدار اللوجستي من الصفر، مع مقاييس التقييم الصحيحة.",
        summary_en="kNN and logistic regression from scratch, with the right evaluation metrics.",
        explanation_ar="""في التصنيف **الدقة وحدها تكذب**. إن كان 95٪ من العينات سالبة، فنموذج يقول
"سالب" دائماً يحقق دقة 95٪ وهو بلا قيمة.

مصفوفة الالتباس (confusion matrix) تكشف الحقيقة:

- `TP` صحيح موجب، `FP` خاطئ موجب، `TN` صحيح سالب، `FN` خاطئ سالب،
- `precision = TP / (TP + FP)` — من النتائج التي أعلنّاها موجبة، كم كان صحيحاً؟
- `recall = TP / (TP + FN)` — من الموجبات الحقيقية، كم التقطنا؟
- `F1` المتوسط التوافقي بينهما، مفيد عند اختلال التوازن.

خوارزميتان للبدء:
- **kNN**: لا تدرّب شيئاً؛ تحسب المسافة لأقرب `k` جيران وتصوّت. بسيط لكنه بطيء عند التنبؤ
  ويحتاج توحيد الميزات.
- **الانحدار اللوجستي**: `sigmoid(Xw) = 1/(1+e^{-z})`، يُدرَّب بتقليل
  الانتروبيا المتقاطعة الثنائية. سريع ويعطي احتمالات قابلة للتفسير.""",
        explanation_en="""In classification **accuracy alone lies**. If 95% of samples are negative, a model that
always says "negative" scores 95% and is worthless.

The confusion matrix tells the truth:

- `TP` true positive, `FP` false positive, `TN` true negative, `FN` false negative,
- `precision = TP / (TP + FP)` - of the cases we flagged, how many were right?
- `recall = TP / (TP + FN)` - of the real positives, how many did we catch?
- `F1` is their harmonic mean, useful under class imbalance.

Two algorithms to start with:
- **kNN**: no training at all; measure the distance to the `k` nearest neighbours and vote.
  Simple, but slow at prediction time and needs scaled features.
- **Logistic regression**: `sigmoid(Xw) = 1/(1+e^{-z})`, trained by minimising binary
  cross-entropy. Fast, and it produces interpretable probabilities.""",
        skills=("ml.classification", "ml.metrics", "ml.logistic"),
        prerequisites=("l7.ml_fundamentals",),
        example_code="""import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

X, y = make_classification(n_samples=600, n_features=4, n_redundant=0, random_state=7)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=7)

scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

for name, model in [
    ("knn(k=5)", KNeighborsClassifier(n_neighbors=5)),
    ("logistic", LogisticRegression(max_iter=1000)),
]:
    model.fit(X_train_s, y_train)
    predictions = model.predict(X_test_s)
    print(f"{name:>9}  accuracy={accuracy_score(y_test, predictions):.3f}  f1={f1_score(y_test, predictions):.3f}")

print("confusion matrix:\\n", confusion_matrix(y_test, LogisticRegression(max_iter=1000).fit(X_train_s, y_train).predict(X_test_s)))
prior = max(y_test.mean(), 1 - y_test.mean())
print("always-guess baseline accuracy:", round(prior, 3))
""",
        example_notes_ar="قارن دائماً مع خط الأساس (تخمين الأغلبية) قبل أن تحتفل بدقة 0.9.",
        example_notes_en="Always compare against the majority-class baseline before celebrating an accuracy of 0.9.",
        experiment_code="""import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=800, n_features=4, weights=[0.9, 0.1], random_state=11)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=11, stratify=y)

model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
probabilities = model.predict_proba(X_test)[:, 1]

print(f"{'threshold':>9} {'precision':>10} {'recall':>8} {'flagged':>8}")
for threshold in (0.2, 0.35, 0.5, 0.7, 0.9):
    flagged = (probabilities >= threshold).astype(int)
    print(f"{threshold:>9.2f} {precision_score(y_test, flagged, zero_division=0):>10.3f} "
          f"{recall_score(y_test, flagged):>8.3f} {int(flagged.sum()):>8}")

print("\\naccuracy of the always-negative model:", round(1 - y_test.mean(), 3))
""",
        experiment_brief_ar="اختر العتبة المناسبة إن كان الثمن مختلفاً بين الخطأين، وفسّر اختيارك.",
        experiment_brief_en="Pick the threshold appropriate when the two error types have different costs, and justify your choice.",
        task=TaskSpec(
            brief_ar="""اكتب (numpy فقط):
1. `knn_predict(X_train, y_train, X_query, k=3)` تُعيد تسميات الاستعلام بأغلبية الأصوات
   (المسافة الإقليدية، ولا تعتمد على sklearn).
2. `accuracy(y_true, y_pred)` نسبة التطابق.
3. `confusion(y_true, y_pred)` تُعيد قاموساً `{"tp", "fp", "tn", "fn"}`.
4. `precision_recall_f1(y_true, y_pred)` تُعيد `{"precision", "recall", "f1"}`
   مع حماية من القسمة على صفر.""",
            brief_en="""Write (numpy only):
1. `knn_predict(X_train, y_train, X_query, k=3)` returning labels by majority vote
   (Euclidean distance, no sklearn).
2. `accuracy(y_true, y_pred)` - the fraction of matches.
3. `confusion(y_true, y_pred)` returning a dict `{"tp", "fp", "tn", "fn"}`.
4. `precision_recall_f1(y_true, y_pred)` returning `{"precision", "recall", "f1"}`,
   guarded against division by zero.""",
            starter_code="""import numpy as np


def knn_predict(X_train, y_train, X_query, k=3):
    pass


def accuracy(y_true, y_pred):
    pass


def confusion(y_true, y_pred):
    pass


def precision_recall_f1(y_true, y_pred):
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import knn_predict

def test_knn_obvious_case():
    X_train = np.array([[0.0], [0.1], [10.0], [10.1]])
    y_train = np.array([0, 0, 1, 1])
    assert knn_predict(X_train, y_train, np.array([[0.05]]), k=3).tolist() == [0]
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import knn_predict, accuracy, confusion, precision_recall_f1

X_TRAIN = np.array([[0.0, 0.0], [0.1, 0.2], [5.0, 5.0], [5.2, 4.9]])
Y_TRAIN = np.array([0, 0, 1, 1])

def test_knn_two_queries():
    queries = np.array([[0.0, 0.0], [5.1, 5.0]])
    assert knn_predict(X_TRAIN, Y_TRAIN, queries, k=3).tolist() == [0, 1]

def test_knn_k_one():
    assert knn_predict(X_TRAIN, Y_TRAIN, np.array([[5.0, 5.0]]), k=1).tolist() == [1]

def test_knn_higher_than_training():
    assert knn_predict(X_TRAIN, Y_TRAIN, np.array([[0.0]]), k=10).tolist() == [0]

def test_accuracy():
    assert accuracy(np.array([1, 0, 1]), np.array([1, 1, 1])) == 2 / 3

def test_accuracy_perfect_and_zero():
    y = np.array([1, 0])
    assert accuracy(y, y) == 1.0
    assert accuracy(y, 1 - y) == 0.0

def test_confusion():
    counts = confusion(np.array([1, 1, 0, 0]), np.array([1, 0, 0, 0]))
    assert counts == {"tp": 1, "fp": 0, "tn": 2, "fn": 1}

def test_confusion_all_correct():
    y = np.array([1, 0, 1])
    assert confusion(y, y)["fp"] == 0

def test_metrics_perfect():
    metrics = precision_recall_f1(np.array([1, 1, 0]), np.array([1, 1, 0]))
    assert metrics["precision"] == 1.0 and metrics["recall"] == 1.0 and metrics["f1"] == 1.0

def test_metrics_no_predictions():
    metrics = precision_recall_f1(np.array([1, 0, 1]), np.array([0, 0, 0]))
    assert metrics["precision"] == 0.0 and metrics["recall"] == 0.0 and metrics["f1"] == 0.0

def test_metrics_mixed():
    metrics = precision_recall_f1(np.array([1, 1, 0, 0]), np.array([1, 0, 0, 0]))
    assert abs(metrics["precision"] - 1.0) < 1e-9
    assert abs(metrics["recall"] - 0.5) < 1e-9
    assert abs(metrics["f1"] - 2/3) < 1e-9
"""},
            reference_solution="""import numpy as np


def knn_predict(X_train, y_train, X_query, k=3):
    train = np.asarray(X_train, dtype=float)
    if train.ndim == 1:
        train = train.reshape(-1, 1)
    query = np.asarray(X_query, dtype=float)
    if query.ndim == 1:
        query = query.reshape(-1, 1)
    labels = np.asarray(y_train)
    neighbours = max(1, min(int(k), len(train)))
    predictions = []
    for point in query:
        distances = np.sqrt(((train - point) ** 2).sum(axis=1))
        nearest = np.argsort(distances)[:neighbours]
        votes = labels[nearest]
        values, counts = np.unique(votes, return_counts=True)
        predictions.append(values[np.argmax(counts)])
    return np.asarray(predictions)


def accuracy(y_true, y_pred):
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    if len(actual) == 0:
        return 0.0
    return float((actual == predicted).sum() / len(actual))


def confusion(y_true, y_pred):
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    return {
        "tp": int(((actual == 1) & (predicted == 1)).sum()),
        "fp": int(((actual == 0) & (predicted == 1)).sum()),
        "tn": int(((actual == 0) & (predicted == 0)).sum()),
        "fn": int(((actual == 1) & (predicted == 0)).sum()),
    }


def precision_recall_f1(y_true, y_pred):
    counts = confusion(y_true, y_pred)
    denominator_precision = counts["tp"] + counts["fp"]
    denominator_recall = counts["tp"] + counts["fn"]
    precision = counts["tp"] / denominator_precision if denominator_precision else 0.0
    recall = counts["tp"] / denominator_recall if denominator_recall else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": float(precision), "recall": float(recall), "f1": float(f1)}
""",
            hints=(
                "Broadcast the query point against the training matrix to get all distances at once.",
                "`np.unique(..., return_counts=True)` is the shortest majority vote.",
                "Clamp `k` to the training size so large k values do not crash.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب انحداراً لوجستياً من الصفر كصنف `LogisticRegressionScratch`:
- `sigmoid(z)` مستقر رقمياً،
- `fit(X, y, learning_rate=0.1, epochs=1000)` بالنزول التدريجي على الانتروبيا المتقاطعة،
- `predict_proba(X)` تُعيد احتمالات بين 0 و1،
- `predict(X, threshold=0.5)` تُعيد تسميات 0/1،
- `loss_history_` قائمة بالخسارة بعد كل حقبة.

دعه يعمل على بيانات موحّدة ويتعامل مع أكثر من ميزة.""",
            brief_en="""Write logistic regression from scratch as a `LogisticRegressionScratch` class:
- `sigmoid(z)` that is numerically stable,
- `fit(X, y, learning_rate=0.1, epochs=1000)` by gradient descent on cross-entropy,
- `predict_proba(X)` returning probabilities between 0 and 1,
- `predict(X, threshold=0.5)` returning 0/1 labels,
- `loss_history_` - the loss after every epoch.

It must work on scaled data and handle more than one feature.""",
            independent=True,
            starter_code="""import numpy as np


class LogisticRegressionScratch:
    def __init__(self):
        pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import LogisticRegressionScratch

def test_probabilities_are_valid():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(60, 2))
    y = (X[:, 0] > 0).astype(int)
    model = LogisticRegressionScratch().fit(X, y, epochs=200)
    probabilities = model.predict_proba(X)
    assert probabilities.min() >= 0 and probabilities.max() <= 1
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import LogisticRegressionScratch

def separable(n=200, seed=5):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 2))
    y = (X[:, 0] + 0.5 * X[:, 1] > 0).astype(int)
    return X, y

def test_trains_to_high_accuracy():
    X, y = separable()
    model = LogisticRegressionScratch().fit(X, y, learning_rate=0.5, epochs=2000)
    assert (model.predict(X) == y).mean() > 0.9

def test_loss_decreases():
    X, y = separable()
    model = LogisticRegressionScratch().fit(X, y, learning_rate=0.5, epochs=300)
    assert len(model.loss_history_) == 300
    assert model.loss_history_[-1] < model.loss_history_[0]

def test_threshold_changes_predictions():
    X, y = separable(100)
    model = LogisticRegressionScratch().fit(X, y, learning_rate=0.5, epochs=800)
    strict = model.predict(X, threshold=0.9).sum()
    loose = model.predict(X, threshold=0.1).sum()
    assert loose >= strict

def test_sigmoid_extremes():
    model = LogisticRegressionScratch().fit(*separable(80), learning_rate=0.5, epochs=100)
    extreme = np.array([[1e6, 1e6], [-1e6, -1e6]])
    probabilities = model.predict_proba(extreme)
    assert np.all(np.isfinite(probabilities))
    assert probabilities.min() >= 0.0 and probabilities.max() <= 1.0

def test_single_feature():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(80, 1))
    y = (X.ravel() > 0).astype(int)
    model = LogisticRegressionScratch().fit(X, y, learning_rate=0.5, epochs=1000)
    assert (model.predict(X) == y).mean() > 0.85

def test_predict_shape():
    X, y = separable(50)
    model = LogisticRegressionScratch().fit(X, y, epochs=50)
    assert model.predict(X).shape == (50,)
"""},
            reference_solution="""import numpy as np


class LogisticRegressionScratch:
    def __init__(self):
        self.weights = None
        self.loss_history_ = []

    @staticmethod
    def sigmoid(z):
        z = np.clip(np.asarray(z, dtype=float), -500, 500)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, X, y, learning_rate=0.1, epochs=1000):
        data = np.asarray(X, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        design = np.hstack([data, np.ones((len(data), 1))])
        target = np.asarray(y, dtype=float)
        self.weights = np.zeros(design.shape[1])
        epsilon = 1e-12
        for _ in range(int(epochs)):
            probabilities = self.sigmoid(design @ self.weights)
            gradient = design.T @ (probabilities - target) / len(design)
            self.weights -= float(learning_rate) * gradient
            clipped = np.clip(probabilities, epsilon, 1 - epsilon)
            loss = float(-(target * np.log(clipped) + (1 - target) * np.log(1 - clipped)).mean())
            self.loss_history_.append(loss)
        return self

    def predict_proba(self, X):
        data = np.asarray(X, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        design = np.hstack([data, np.ones((len(data), 1))])
        return self.sigmoid(design @ self.weights)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)
""",
        ),
        transfer_ar="استخدم الانحدار اللوجستي في Neural Civilization لتصنيف سلوك الوكلاء.",
        transfer_en="Use logistic regression in Neural Civilization to classify agent behaviour.",
        references=(
            ("scikit-learn - metrics", "https://scikit-learn.org/stable/modules/model_evaluation.html"),
            ("Logistic regression on Wikipedia", "https://en.wikipedia.org/wiki/Logistic_regression"),
        ),
    ),
    CurriculumModule(
        id="l7.evaluation_cv",
        level=7,
        order_index=3,
        domain="machine_learning",
        title_ar="التحقق المتقاطع واختيار النموذج",
        title_en="Cross-validation and model selection",
        summary_ar="منحنيات التعلّم، k-fold، والبحث عن المعاملات الفائقة.",
        summary_en="Learning curves, k-fold splits and hyperparameter search.",
        explanation_ar="""تقسيم واحد train/test يعطي رقماً واحداً لا تعرف مدى ثباته. **التحقق المتقاطع** يعطيك
توزيعاً: قسّم البيانات إلى `k` أجزاء، درّب على `k-1` واختبر على الجزء المتبقي، وكرّر.

- `k=5` أو `10` هما المعيار. كلما كبر `k` قلّ الانحياز وزاد التكلفة الحسابية.
- للتصنيف غير المتوازن استخدم **تقسيماً طبقياً** (stratified) يحفظ نسبة الأصناف.
- للبيانات الزمنية لا تستخدم k-fold العشوائي: استخدم تقسيماً زمنياً (الماضي للتدريب،
  المستقبل للاختبار).

**منحنى التعلّم** أهم أداة تشخيص: ارسم خطأ التدريب وخطأ التحقق مقابل حجم بيانات التدريب.
- منحنيان قريبان وخطأ عالٍ → **عدم ملائمة (underfitting)**: زِد تعقيد النموذج.
- فجوة كبيرة بينهما → **تعلّم زائد (overfitting)**: زِد البيانات أو قوّي التنظيم.
- انخفاض الفجوة مع المزيد من البيانات → البيانات ستساعدك.""",
        explanation_en="""A single train/test split gives one number with unknown stability. **Cross-validation**
gives you a distribution: split into `k` folds, train on `k-1`, test on the held-out fold and
repeat.

- `k=5` or `10` is the standard. Larger `k` means less bias and more compute.
- For imbalanced classification use a **stratified** split that preserves class ratios.
- For time series, never use a random k-fold: split by time (past trains, future tests).

The **learning curve** is the key diagnostic: plot training and validation error against the
training-set size.
- curves close together but high -> **underfitting**: raise model complexity.
- a wide gap between them -> **overfitting**: add data or strengthen regularisation.
- the gap shrinking with more data -> more data will help.""",
        skills=("ml.cross_validation", "ml.model_selection", "ml.evaluation"),
        prerequisites=("l7.classification",),
        example_code="""import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

X, y = make_regression(n_samples=300, n_features=1, noise=18, random_state=2)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=2)

print(f"{'degree':>6} {'train RMSE':>11} {'test RMSE':>10} {'cv mean':>9} {'cv std':>8}")
for degree in (1, 2, 4, 8, 12):
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X_train, y_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, model.predict(X_train)))
    test_rmse = np.sqrt(mean_squared_error(y_test, model.predict(X_test)))
    scores = -cross_val_score(model, X_train, y_train,
                              scoring="neg_root_mean_squared_error", cv=KFold(5, shuffle=True, random_state=0))
    print(f"{degree:>6} {train_rmse:>11.2f} {test_rmse:>10.2f} {scores.mean():>9.2f} {scores.std():>8.2f}")

print("\\nlarge train/test gap plus a rising test error is overfitting.")
""",
        example_notes_ar="لاحظ كيف تستمر درجة التدريب في التحسّن بينما يسوء خطأ الاختبار — علامة التعلّم الزائد.",
        example_notes_en="Watch training error keep improving while test error gets worse - the overfitting signature.",
        experiment_code="""import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import learning_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_classification(n_samples=800, n_features=8, n_informative=4, random_state=4)
pipeline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.1))

sizes, train_scores, val_scores = learning_curve(
    pipeline, X, y, train_sizes=[0.1, 0.25, 0.5, 0.75, 1.0], cv=5, scoring="accuracy"
)

print(f"{'samples':>8} {'train acc':>10} {'cv acc':>8} {'gap':>7}")
for size, train, val in zip(sizes, train_scores.mean(axis=1), val_scores.mean(axis=1)):
    print(f"{size:>8} {train:>10.3f} {val:>8.3f} {train - val:>7.3f}")
""",
        experiment_brief_ar="زد `C` إلى 100 وشاهد كيف تتغيّر الفجوة، وفسّر ذلك بدور التنظيم.",
        experiment_brief_en="Raise `C` to 100 and watch the gap change, then explain it in terms of regularisation.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `kfold_indices(n, k=5, seed=0)` تُعيد قائمة `(train_idx, val_idx)` بطول `k`
   بتقسيم مختلط محدّد بالبذرة.
2. `cross_val_score(make_model, X, y, k=5, seed=0)` تُدرّب `make_model()` على كل طية
   وتُعيد قائمة الدرجات (الدقة للتصنيف، `1 - rmse` للانحدار: استخدم الدقة دائماً).
3. `summarise(scores)` تُعيد `{"mean", "std", "min", "max"}`.
4. `detect_overfitting(train_score, val_score, tolerance=0.1)` تُعيد `True` إذا كانت
   الفجوة أكبر من `tolerance`.""",
            brief_en="""Write:
1. `kfold_indices(n, k=5, seed=0)` returning a list of `(train_idx, val_idx)` of length `k`,
   with a seeded shuffle.
2. `cross_val_score(make_model, X, y, k=5, seed=0)` training `make_model()` on every fold and
   returning the list of accuracy scores.
3. `summarise(scores)` returning `{"mean", "std", "min", "max"}`.
4. `detect_overfitting(train_score, val_score, tolerance=0.1)` returning `True` when the gap
   exceeds `tolerance`.""",
            starter_code="""import numpy as np


def kfold_indices(n, k=5, seed=0):
    pass


def cross_val_score(make_model, X, y, k=5, seed=0):
    pass


def summarise(scores):
    pass


def detect_overfitting(train_score, val_score, tolerance=0.1):
    pass
""",
            public_tests={"test_public.py": """from main import kfold_indices

def test_fold_count():
    folds = kfold_indices(50, k=5, seed=0)
    assert len(folds) == 5
    assert all(len(train) + len(val) == 50 for train, val in folds)
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import kfold_indices, cross_val_score, summarise, detect_overfitting

class Constant:
    \"\"\"Always predicts the majority class of the training fold.\"\"\"

    def fit(self, X, y):
        self.value = int(round(float(np.mean(y))))
        return self

    def predict(self, X):
        return np.full(len(X), self.value)

def test_folds_cover_every_row():
    folds = kfold_indices(20, k=4, seed=3)
    seen = np.concatenate([val for _, val in folds])
    assert sorted(seen.tolist()) == list(range(20))

def test_folds_are_deterministic():
    first, second = kfold_indices(30, k=3, seed=1), kfold_indices(30, k=3, seed=1)
    for (train_a, val_a), (train_b, val_b) in zip(first, second):
        assert np.array_equal(train_a, train_b)
        assert np.array_equal(val_a, val_b)

def test_no_train_val_overlap():
    for train, val in kfold_indices(40, k=5, seed=2):
        assert not set(train.tolist()) & set(val.tolist())

def test_cross_val_returns_one_score_per_fold():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, 2))
    y = (X[:, 0] > 0).astype(int)
    scores = cross_val_score(Constant, X, y, k=5, seed=0)
    assert len(scores) == 5
    assert all(0.0 <= score <= 1.0 for score in scores)

def test_summarise():
    summary = summarise([0.8, 0.9, 1.0])
    assert abs(summary["mean"] - 0.9) < 1e-9
    assert summary["min"] == 0.8 and summary["max"] == 1.0
    assert summary["std"] > 0

def test_summarise_single():
    summary = summarise([0.5])
    assert summary["std"] == 0.0

def test_overfitting_detection():
    assert detect_overfitting(0.99, 0.7) is True
    assert detect_overfitting(0.8, 0.77) is False

def test_overfitting_custom_tolerance():
    assert detect_overfitting(0.9, 0.8, tolerance=0.05) is True
    assert detect_overfitting(0.9, 0.8, tolerance=0.2) is False
"""},
            reference_solution="""import numpy as np


def kfold_indices(n, k=5, seed=0):
    rng = np.random.default_rng(seed)
    order = rng.permutation(int(n))
    folds = []
    for fold in range(int(k)):
        validation = order[fold::k]
        train = np.setdiff1d(order, validation)
        folds.append((train, validation))
    return folds


def cross_val_score(make_model, X, y, k=5, seed=0):
    X = np.asarray(X)
    y = np.asarray(y)
    scores = []
    for train, validation in kfold_indices(len(X), k=k, seed=seed):
        model = make_model()
        model.fit(X[train], y[train])
        predictions = np.asarray(model.predict(X[validation]))
        scores.append(float((predictions == np.asarray(y)[validation]).mean()))
    return scores


def summarise(scores):
    values = np.asarray(list(scores), dtype=float)
    if values.size == 0:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": float(values.mean()),
        "std": float(values.std()),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def detect_overfitting(train_score, val_score, tolerance=0.1):
    return (train_score - val_score) > tolerance
""",
            hints=(
                "`order[fold::k]` is the shortest way to slice a permutation into k folds.",
                "`np.setdiff1d` gives the training complement of the validation indices.",
                "`make_model()` is a factory: call it fresh inside every fold.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `grid_search(make_model, param_grid, X, y, k=5, seed=0)` حيث `param_grid`
قاموس `{"اسم_المعامل": [قيم]}` و`make_model(**params)` يُعيد نموذجاً بواجهتي
`fit` و`predict`. تُعيد الدالة:

```python
{"best_params": {...}, "best_score": float, "results": [{"params": ..., "mean": ..., "std": ...}]}
```

مرّ على كل التوليفات (`itertools.product`) مع الحفاظ على ترتيب المفاتيح.""",
            brief_en="""Write `grid_search(make_model, param_grid, X, y, k=5, seed=0)` where `param_grid` is a dict
of `{"name": [values]}` and `make_model(**params)` returns a model with `fit` and `predict`.
Return:

```python
{"best_params": {...}, "best_score": float, "results": [{"params": ..., "mean": ..., "std": ...}]}
```

Walk every combination (`itertools.product`) while keeping the key order stable.""",
            independent=True,
            starter_code="""import itertools


def grid_search(make_model, param_grid, X, y, k=5, seed=0):
    pass
""",
            public_tests={"test_public.py": """from main import grid_search

class Threshold:
    def __init__(self, cut=0.0):
        self.cut = cut

    def fit(self, X, y):
        return self

    def predict(self, X):
        return [1 if row[0] > self.cut else 0 for row in X]

def test_grid_search_runs():
    X = [[0.0], [1.0], [2.0], [3.0]]
    y = [0, 0, 1, 1]
    report = grid_search(Threshold, {"cut": [0.5, 1.5, 2.5]}, X, y, k=2, seed=0)
    assert set(report) == {"best_params", "best_score", "results"}
    assert len(report["results"]) == 3
"""},
            hidden_tests={"test_hidden.py": """from main import grid_search

class Threshold:
    def __init__(self, cut=0.0, invert=False):
        self.cut = cut
        self.invert = invert

    def fit(self, X, y):
        return self

    def predict(self, X):
        flags = [1 if row[0] > self.cut else 0 for row in X]
        return [1 - flag for flag in flags] if self.invert else flags

X = [[float(i)] for i in range(20)]
y = [0] * 10 + [1] * 10

def test_best_params_found():
    report = grid_search(Threshold, {"cut": [4.5, 9.5, 14.5]}, X, y, k=4, seed=0)
    assert report["best_params"]["cut"] == 9.5
    assert report["best_score"] == 1.0

def test_two_parameters():
    report = grid_search(Threshold, {"cut": [9.5], "invert": [False, True]}, X, y, k=4, seed=0)
    assert len(report["results"]) == 2
    assert report["best_params"]["invert"] is False

def test_results_carry_std():
    report = grid_search(Threshold, {"cut": [9.5, 0.0]}, X, y, k=4, seed=0)
    for entry in report["results"]:
        assert set(entry) == {"params", "mean", "std"}

def test_empty_grid():
    report = grid_search(Threshold, {}, X, y, k=2, seed=0)
    assert report["best_params"] == {}
    assert len(report["results"]) == 1

def test_best_score_is_max_of_means():
    report = grid_search(Threshold, {"cut": [9.5, 0.0, 15.0]}, X, y, k=5, seed=1)
    assert report["best_score"] == max(entry["mean"] for entry in report["results"])
"""},
            reference_solution="""import itertools

import numpy as np


def grid_search(make_model, param_grid, X, y, k=5, seed=0):
    X = np.asarray(X)
    y = np.asarray(y)
    names = list(param_grid)
    combinations = [
        dict(zip(names, values)) for values in itertools.product(*(param_grid[name] for name in names))
    ]
    results = []
    for params in combinations:
        scores = []
        rng = np.random.default_rng(seed)
        order = rng.permutation(len(X))
        for fold in range(int(k)):
            validation = order[fold::k]
            train = np.setdiff1d(order, validation)
            model = make_model(**params)
            model.fit(X[train], y[train])
            predictions = np.asarray(model.predict(X[validation]))
            scores.append(float((predictions == y[validation]).mean()))
        values = np.asarray(scores, dtype=float)
        results.append({
            "params": params,
            "mean": float(values.mean()) if values.size else 0.0,
            "std": float(values.std()) if values.size else 0.0,
        })
    best = max(results, key=lambda entry: entry["mean"]) if results else {"params": {}, "mean": 0.0}
    return {"best_params": best["params"], "best_score": best["mean"], "results": results}
""",
        ),
        transfer_ar="استخدم `grid_search` في Model Olympics لاختيار إعدادات نموذجك.",
        transfer_en="Use `grid_search` in Model Olympics to tune your model settings.",
        references=(
            ("scikit-learn - cross validation", "https://scikit-learn.org/stable/modules/cross_validation.html"),
            ("scikit-learn - learning curves", "https://scikit-learn.org/stable/modules/learning_curve.html"),
        ),
    ),
]
