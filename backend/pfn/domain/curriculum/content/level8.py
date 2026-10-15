"""LEVEL 8 - Neural networks from scratch."""

from __future__ import annotations

from pfn.domain.curriculum.models import CurriculumModule, TaskSpec

MODULES: list[CurriculumModule] = [
    CurriculumModule(
        id="l8.neural_from_scratch",
        level=8,
        order_index=1,
        domain="deep_learning",
        title_ar="شبكة عصبية من الصفر",
        title_en="A neural network from scratch",
        summary_ar="طبقات، أوزان، دوال تنشيط، وتمرير أمامي — بـ numpy فقط.",
        summary_en="Layers, weights, activations and a forward pass - numpy only.",
        explanation_ar="""الشبكة العصبية سلسلة تحويلات خطية مع دوال غير خطية بينها:

```
z = X @ W + b        # تحويل خطي
a = activation(z)    # لاخطية
```

بدون اللاخطية تبقى الشبكة مجرد انحدار خطي مهما كثرت طبقاتها.

دوال التنشيط:
- `sigmoid` للاحتمالات الثنائية (تعاني من تلاشي التدرج)،
- `tanh` مركزي حول الصفر،
- `ReLU = max(0, z)` الافتراضي للطبقات المخفية (سريع، لكن قد يموت العصبون)،
- `softmax` لتحويل المخرجات إلى توزيع احتمالي متعدد الأصناف.

التهيئة مهمة: أوزان صفرية تجعل كل العصبونات متطابقة (لا تتعلّم شيئاً).
استخدم تهيئة عشوائية صغيرة، أو `He`/`Glorot` حسب دالة التنشيط.

دالة الخسارة:
- `MSE` للانحدار،
- الانتروبيا المتقاطعة (`cross-entropy`) للتصنيف.""",
        explanation_en="""A neural network is a chain of linear transforms with non-linearities in between:

```
z = X @ W + b        # linear
a = activation(z)    # non-linear
```

Without the non-linearity the network collapses into a plain linear model no matter how many
layers it has.

Activations:
- `sigmoid` for binary probabilities (suffers from vanishing gradients),
- `tanh` is centred around zero,
- `ReLU = max(0, z)` is the default for hidden layers (fast, but units can die),
- `softmax` turns outputs into a multi-class probability distribution.

Initialisation matters: all-zero weights make every unit identical and nothing is learned.
Use small random values, or `He`/`Glorot` depending on the activation.

Losses:
- `MSE` for regression,
- cross-entropy for classification.""",
        skills=("dl.nn", "dl.tensors"),
        prerequisites=("l7.classification",),
        example_code="""import numpy as np


def dense_forward(X, weights, bias):
    return X @ weights + bias


def relu(z):
    return np.maximum(0, z)


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def softmax(z):
    shifted = z - z.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


rng = np.random.default_rng(0)
X = rng.normal(size=(4, 3))

W1 = rng.normal(scale=0.5, size=(3, 5))
b1 = np.zeros(5)
W2 = rng.normal(scale=0.5, size=(5, 2))
b2 = np.zeros(2)

hidden = relu(dense_forward(X, W1, b1))
logits = dense_forward(hidden, W2, b2)
probabilities = softmax(logits)

print("input        :", X.shape)
print("hidden (relu):", hidden.shape)
print("logits       :", np.round(logits, 3))
print("softmax rows sum to one:", np.allclose(probabilities.sum(axis=1), 1.0))
print("sigmoid(0)   :", sigmoid(np.array([0.0]))[0])
print("relu(-1), relu(1):", relu(np.array([-1.0]))[0], relu(np.array([1.0]))[0])
""",
        example_notes_ar="`softmax` يطرح الأكبر قبل الأسّ لتجنّب الفيضان (overflow).",
        example_notes_en="`softmax` subtracts the row maximum before exponentiating to avoid overflow.",
        experiment_code="""import numpy as np


def init_layer(inputs, outputs, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(scale=np.sqrt(2.0 / inputs), size=(inputs, outputs)), np.zeros(outputs)


def forward(X, params, activation):
    out = X
    for index, (W, b) in enumerate(params):
        z = out @ W + b
        out = activation(z) if index < len(params) - 1 else z
    return out


rng = np.random.default_rng(1)
X = rng.normal(size=(200, 4))
shapes = [(4, 16), (16, 8), (8, 1)]
params = [init_layer(a, b, seed=i) for i, (a, b) in enumerate(shapes)]

for name, activation in [("relu", lambda z: np.maximum(0, z)), ("tanh", np.tanh)]:
    out = forward(X, params, activation)
    print(f"{name:>4}: mean {out.mean():8.4f}  std {out.std():7.4f}  dead units "
          f"{int((np.abs(out) < 1e-9).mean() * 100)}%")

zeros = [(np.zeros_like(W), np.zeros_like(b)) for W, b in params]
out = forward(X, zeros, np.tanh)
print("all-zero init std:", round(float(out.std()), 6), "  <- no signal, nothing to learn")
""",
        experiment_brief_ar="غيّر مقياس التهيئة إلى 5.0 وشاهد كيف تشبع المخرجات، وفسّر السبب.",
        experiment_brief_en="Change the initialisation scale to 5.0 and watch the outputs saturate, then explain why.",
        task=TaskSpec(
            brief_ar="""اكتب (numpy فقط):
1. `dense(X, W, b)` التحويل الخطي.
2. `relu(z)`, `sigmoid(z)`, `tanh_activation(z)`, `softmax(z)`.
3. `forward(X, layers)` حيث `layers` قائمة `(W, b)`؛ آخر طبقة بلا تنشيط
   والطبقات المخفية بـ ReLU. تُعيد `(logits, hidden_states)` حيث `hidden_states`
   قائمة مخرجات كل طبقة بعد التنشيط (بما فيها المدخل).
4. `cross_entropy(y_true, probabilities)` بمتوسط الخسارة مع حماية `epsilon`.""",
            brief_en="""Write (numpy only):
1. `dense(X, W, b)` - the linear transform.
2. `relu(z)`, `sigmoid(z)`, `tanh_activation(z)` and `softmax(z)`.
3. `forward(X, layers)` where `layers` is a list of `(W, b)`; the last layer has no activation
   and hidden layers use ReLU. Return `(logits, hidden_states)` where `hidden_states` holds the
   output of every layer after activation (including the input).
4. `cross_entropy(y_true, probabilities)` - the mean loss, guarded with an `epsilon`.""",
            starter_code="""import numpy as np


def dense(X, W, b):
    pass


def relu(z):
    pass


def sigmoid(z):
    pass


def tanh_activation(z):
    pass


def softmax(z):
    pass


def forward(X, layers):
    pass


def cross_entropy(y_true, probabilities):
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import dense, relu

def test_dense():
    X = np.array([[1.0, 2.0]])
    W = np.array([[1.0], [1.0]])
    b = np.array([0.5])
    assert np.allclose(dense(X, W, b), [[3.5]])

def test_relu():
    assert relu(np.array([-2.0, 0.0, 3.0])).tolist() == [0.0, 0.0, 3.0]
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import dense, relu, sigmoid, tanh_activation, softmax, forward, cross_entropy

def test_sigmoid_range_and_centre():
    values = sigmoid(np.array([-1000.0, 0.0, 1000.0]))
    assert values.min() >= 0.0 and values.max() <= 1.0
    assert abs(values[1] - 0.5) < 1e-9

def test_tanh_range():
    values = tanh_activation(np.array([-1000.0, 0.0, 1000.0]))
    assert abs(values[1]) < 1e-9 and abs(values[2] - 1.0) < 1e-6

def test_softmax_sums_to_one():
    probabilities = softmax(np.array([[1.0, 2.0, 3.0], [0.0, 0.0, 0.0]]))
    assert np.allclose(probabilities.sum(axis=1), [1.0, 1.0])
    assert np.argmax(probabilities[0]) == 2

def test_softmax_is_stable():
    probabilities = softmax(np.array([[1000.0, 1001.0]]))
    assert np.all(np.isfinite(probabilities))

def test_forward_shapes():
    rng = np.random.default_rng(0)
    layers = [(rng.normal(size=(3, 4)), np.zeros(4)), (rng.normal(size=(4, 2)), np.zeros(2))]
    logits, states = forward(rng.normal(size=(5, 3)), layers)
    assert logits.shape == (5, 2)
    assert len(states) == 3
    assert states[0].shape == (5, 3) and states[1].shape == (5, 4) and states[2].shape == (5, 2)

def test_forward_uses_relu():
    rng = np.random.default_rng(1)
    layers = [(rng.normal(size=(2, 4)), np.zeros(4)), (rng.normal(size=(4, 2)), np.zeros(2))]
    logits, states = forward(np.array([[-5.0, 5.0]]), layers)
    assert np.all(states[1] >= 0)          # hidden layer is ReLU
    assert np.any(logits < 0)              # output layer stays linear

def test_forward_single_layer_is_linear():
    W = np.array([[1.0], [2.0]])
    b = np.array([3.0])
    logits, _ = forward(np.array([[1.0, 1.0]]), [(W, b)])
    assert np.allclose(logits, [[6.0]])

def test_cross_entropy_perfect_is_zero():
    probabilities = np.array([[0.9, 0.1], [0.2, 0.8]])
    assert cross_entropy(np.array([0, 1]), probabilities) > 0

def test_cross_entropy_confident_correct_is_small():
    probabilities = np.array([[0.999, 0.001]])
    loss = cross_entropy(np.array([0]), probabilities)
    assert loss < 0.01
"""},
            reference_solution="""import numpy as np


def dense(X, W, b):
    return np.asarray(X) @ W + b


def relu(z):
    return np.maximum(0, z)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(z, dtype=float), -500, 500)))


def tanh_activation(z):
    return np.tanh(np.asarray(z, dtype=float))


def softmax(z):
    data = np.asarray(z, dtype=float)
    shifted = data - data.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def forward(X, layers):
    activations = [np.asarray(X, dtype=float)]
    output = activations[0]
    for index, (W, b) in enumerate(layers):
        z = dense(output, W, b)
        output = z if index == len(layers) - 1 else relu(z)
        activations.append(output)
    return output, activations


def cross_entropy(y_true, probabilities):
    labels = np.asarray(y_true, dtype=int).ravel()
    rows = np.arange(labels.size)
    clipped = np.clip(np.asarray(probabilities, dtype=float), 1e-12, 1 - 1e-12)
    return float(-np.log(clipped[rows, labels]).mean())
""",
            hints=(
                "Clip the input of `sigmoid` before exponentiating: `exp(1000)` overflows.",
                "Subtract the row maximum inside `softmax` - it does not change the result.",
                "The final layer output is the logits, so skip the activation for the last index.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `TwoLayerNet` (طبقة مخفية واحدة) يدرّب على XOR بالنزول التدريجي:

- `__init__(hidden=8, learning_rate=0.5, seed=0)` يهيّئ الأوزان بـ He.
- `forward(X)` تُرجع احتمالات sigmoid.
- `fit(X, y, epochs=5000)` تُحدّث الأوزان بالانتشار العكسي
  (انتروبيا متقاطعة ثنائية مع مخرج sigmoid: `dz = (p - y) / n`).
- `predict(X, threshold=0.5)` وخاصية `loss_history_`.

يجب أن يحقق دقة 1.0 على بيانات XOR الأربعة.""",
            brief_en="""Write a `TwoLayerNet` (one hidden layer) trained on XOR by gradient descent:

- `__init__(hidden=8, learning_rate=0.5, seed=0)` initialising weights with He scaling.
- `forward(X)` returning sigmoid probabilities.
- `fit(X, y, epochs=5000)` updating the weights by backpropagation
  (binary cross-entropy with a sigmoid output: `dz = (p - y) / n`).
- `predict(X, threshold=0.5)` and a `loss_history_` list.

It must reach accuracy 1.0 on the four XOR rows.""",
            independent=True,
            starter_code="""import numpy as np


class TwoLayerNet:
    def __init__(self, hidden=8, learning_rate=0.5, seed=0):
        pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import TwoLayerNet

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0, 1, 1, 0])

def test_forward_shape():
    net = TwoLayerNet(hidden=4, seed=0).fit(X, y, epochs=1)
    assert net.forward(X).shape == (4, 1)
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import TwoLayerNet

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
y = np.array([0, 1, 1, 0])

def test_learns_xor():
    net = TwoLayerNet(hidden=8, learning_rate=0.5, seed=0).fit(X, y, epochs=6000)
    assert (net.predict(X).ravel() == y).all()

def test_loss_decreases():
    net = TwoLayerNet(hidden=8, learning_rate=0.5, seed=0).fit(X, y, epochs=800)
    assert len(net.loss_history_) == 800
    assert net.loss_history_[-1] < net.loss_history_[0]

def test_probabilities_in_range():
    net = TwoLayerNet(hidden=6, seed=1).fit(X, y, epochs=500)
    probabilities = net.forward(X)
    assert probabilities.min() > 0.0 and probabilities.max() < 1.0

def test_predict_shape():
    net = TwoLayerNet(hidden=4, seed=2).fit(X, y, epochs=100)
    assert net.predict(X).shape == (4, 1)

def test_different_seeds_all_learn():
    for seed in (0, 1, 2):
        net = TwoLayerNet(hidden=8, learning_rate=0.5, seed=seed).fit(X, y, epochs=6000)
        assert (net.predict(X).ravel() == y).all(), seed
"""},
            reference_solution="""import numpy as np


class TwoLayerNet:
    def __init__(self, hidden=8, learning_rate=0.5, seed=0):
        self.hidden = int(hidden)
        self.learning_rate = float(learning_rate)
        self.seed = int(seed)
        self.loss_history_ = []

    def _init(self, inputs):
        rng = np.random.default_rng(self.seed)
        self.W1 = rng.normal(scale=np.sqrt(2.0 / inputs), size=(inputs, self.hidden))
        self.b1 = np.zeros(self.hidden)
        self.W2 = rng.normal(scale=np.sqrt(2.0 / self.hidden), size=(self.hidden, 1))
        self.b2 = np.zeros(1)

    def forward(self, X):
        data = np.asarray(X, dtype=float)
        self.z1 = data @ self.W1 + self.b1
        self.a1 = np.maximum(0, self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        return 1.0 / (1.0 + np.exp(-np.clip(self.z2, -500, 500)))

    def fit(self, X, y, epochs=5000):
        data = np.asarray(X, dtype=float)
        target = np.asarray(y, dtype=float).reshape(-1, 1)
        self._init(data.shape[1])
        n = len(data)
        for _ in range(int(epochs)):
            probabilities = self.forward(data)
            clipped = np.clip(probabilities, 1e-12, 1 - 1e-12)
            loss = float(-(target * np.log(clipped) + (1 - target) * np.log(1 - clipped)).mean())
            self.loss_history_.append(loss)

            dz2 = (probabilities - target) / n
            dW2 = self.a1.T @ dz2
            db2 = dz2.sum(axis=0)
            da1 = dz2 @ self.W2.T
            dz1 = da1 * (self.z1 > 0)
            dW1 = data.T @ dz1
            db1 = dz1.sum(axis=0)

            self.W2 -= self.learning_rate * dW2
            self.b2 -= self.learning_rate * db2
            self.W1 -= self.learning_rate * dW1
            self.b1 -= self.learning_rate * db1
        return self

    def predict(self, X, threshold=0.5):
        return (self.forward(X) >= threshold).astype(int)
""",
        ),
        transfer_ar="استخدم الشبكة في Neural Civilization لتمثيل سياسة الوكيل.",
        transfer_en="Use the network in Neural Civilization to represent an agent's policy.",
        references=(
            ("Neural networks and deep learning (Nielsen)", "http://neuralnetworksanddeeplearning.com/"),
            ("CS231n - neural networks notes", "https://cs231n.github.io/neural-networks-1/"),
        ),
    ),
    CurriculumModule(
        id="l8.backprop_mlp",
        level=8,
        order_index=2,
        domain="deep_learning",
        title_ar="الانتشار العكسي والتحقق منه",
        title_en="Backpropagation and how to verify it",
        summary_ar="شبكة متعددة الطبقات كاملة مع تحقق عددي من التدرجات.",
        summary_en="A full multi-layer network with numerical gradient checking.",
        explanation_ar="""الانتشار العكسي ليس سوى **قاعدة السلسلة** مطبّقة بترتيب عكسي، مع إعادة استخدام
القيم الوسيطة المحسوبة في التمرير الأمامي.

لشبكة `L` طبقة:
1. احسب `z[l] = a[l-1] W[l] + b[l]` وخزّن `a[l]`،
2. عند المخرج احسب `dz[L] = dL/da · activation'(z[L])` (مع sigmoid + BCE يصبح `p - y`)،
3. انتقل للخلف:
   `dW[l] = a[l-1]ᵀ dz[l]`،
   `db[l] = sum(dz[l])`،
   `dz[l-1] = (dz[l] W[l]ᵀ) · activation'(z[l-1])`.

**التحقق العددي** أهم مهارة هنا. قرّب التدرج:

```
numerical ≈ (loss(w + eps) - loss(w - eps)) / (2 * eps)
```

وقارنه بتدرجك. النسبة الصحيحة أقل من `1e-5` تقريباً. إن كان الفرق كبيراً
فخطأك في مكان ما — وغالباً في مشتق التنشيط أو في الأبعاد.

مقارنة التدرج مكلفة (استدعاءان لكل معامل)، لذلك تُجرى على شبكة صغيرة وعدد قليل
من العينات قبل التدريب الطويل.""",
        explanation_en="""Backpropagation is just the **chain rule** applied in reverse order, reusing the
intermediate values computed during the forward pass.

For a network with `L` layers:
1. compute `z[l] = a[l-1] W[l] + b[l]` and store `a[l]`,
2. at the output compute `dz[L] = dL/da * activation'(z[L])` (with sigmoid + BCE it becomes `p - y`),
3. walk backwards:
   `dW[l] = a[l-1]' dz[l]`,
   `db[l] = sum(dz[l])`,
   `dz[l-1] = (dz[l] W[l]') * activation'(z[l-1])`.

**Gradient checking** is the key skill here. Approximate the gradient with

```
numerical ~= (loss(w + eps) - loss(w - eps)) / (2 * eps)
```

and compare it with yours. A healthy relative error is below roughly `1e-5`. If the gap is
large, there is a bug somewhere - usually in the activation derivative or in the shapes.

Checking is expensive (two evaluations per parameter), so run it on a small network and a few
samples before the long training run.""",
        skills=("dl.autograd", "dl.nn"),
        prerequisites=("l8.neural_from_scratch",),
        example_code="""import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def binary_cross_entropy(y, p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


rng = np.random.default_rng(0)
X = rng.normal(size=(6, 3))
y = rng.integers(0, 2, size=(6, 1)).astype(float)

W1 = rng.normal(scale=0.3, size=(3, 4))
b1 = np.zeros(4)
W2 = rng.normal(scale=0.3, size=(4, 1))
b2 = np.zeros(1)


def forward(X):
    z1 = X @ W1 + b1
    a1 = np.maximum(0, z1)
    z2 = a1 @ W2 + b2
    return z1, a1, z2, sigmoid(z2)


def backward(X, y):
    z1, a1, z2, p = forward(X)
    n = len(X)
    dz2 = (p - y) / n
    dW2 = a1.T @ dz2
    db2 = dz2.sum(axis=0)
    da1 = dz2 @ W2.T
    dz1 = da1 * (z1 > 0)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0)
    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}


def numerical_gradient(index, eps=1e-5):
    W1[index] += eps
    plus = binary_cross_entropy(y, forward(X)[3])
    W1[index] -= 2 * eps
    minus = binary_cross_entropy(y, forward(X)[3])
    W1[index] += eps
    return (plus - minus) / (2 * eps)


analytic = backward(X, y)["W1"]
numeric = np.array([[numerical_gradient((i, j)) for j in range(W1.shape[1])] for i in range(W1.shape[0])])
difference = np.abs(analytic - numeric).max() / np.abs(analytic + numeric).max()
print("max analytic |grad|:", round(float(np.abs(analytic).max()), 8))
print("relative difference:", round(float(difference), 8))
print("gradient check passed:", difference < 1e-5)
""",
        example_notes_ar="التحقق العددي يكلّف استدعاءين لكل معامل: استخدمه للتشخيص فقط.",
        example_notes_en="Numerical checking costs two evaluations per parameter: use it for diagnosis only.",
        experiment_code="""import numpy as np
from sklearn.datasets import make_moons
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

rng = np.random.default_rng(0)


def init(inputs, outputs, seed):
    r = np.random.default_rng(seed)
    return r.normal(scale=np.sqrt(2.0 / inputs), size=(inputs, outputs)), np.zeros(outputs)


W1, b1 = init(2, 16, 1)
W2, b2 = init(16, 1, 2)

for epoch in range(1, 3001):
    z1 = X_train @ W1 + b1
    a1 = np.tanh(z1)
    p = 1 / (1 + np.exp(-(a1 @ W2 + b2)))
    dz2 = (p - y_train.reshape(-1, 1)) / len(X_train)
    dW2 = a1.T @ dz2
    db2 = dz2.sum(axis=0)
    dz1 = (dz2 @ W2.T) * (1 - a1 ** 2)
    dW1 = X_train.T @ dz1
    db1 = dz1.sum(axis=0)
    for param, grad in ((W1, dW1), (b1, db1), (W2, dW2), (b2, db2)):
        param -= 0.5 * grad
    if epoch in (1, 100, 1000, 3000):
        predictions = (p >= 0.5).astype(int).ravel()
        print(f"epoch {epoch:>5}: train accuracy {accuracy_score(y_train, predictions):.3f}")

test_p = 1 / (1 + np.exp(-(np.tanh(X_test @ W1 + b1) @ W2 + b2)))
print("test accuracy:", round(accuracy_score(y_test, (test_p >= 0.5).astype(int).ravel()), 3))
""",
        experiment_brief_ar="بدّل tanh إلى ReLU وقارن سرعة التعلّم والدقة النهائية.",
        experiment_brief_en="Swap tanh for ReLU and compare the learning speed and final accuracy.",
        task=TaskSpec(
            brief_ar="""اكتب:
1. `mlp_forward(X, params, activations)` لشبكة من `L` طبقات: تُعيد `(output, cache)`
   حيث `cache` قائمة `(X_in, z, a)` لكل طبقة. التنشيط يُمرَّر كقائمة دوال بطول `L-1`
   (آخر طبقة خطية).
2. `mlp_backward(y, output, cache, params, activations_derivative)` تُعيد قائمة
   تدرجات بنفس ترتيب `params` (قائمة `(dW, db)`).
3. `numerical_gradient(loss_function, params, index, eps=1e-5)` تُعيد التدرج العددي
   لمعامل واحد (index = `(layer, row, col)` داخل W).
4. `gradient_check(loss_function, params, analytic, eps=1e-5)` تُعيد أكبر فرق نسبي.""",
            brief_en="""Write:
1. `mlp_forward(X, params, activations)` for an `L`-layer network, returning `(output, cache)`
   where `cache` holds `(X_in, z, a)` per layer. `activations` is a list of length `L-1`
   (the last layer is linear).
2. `mlp_backward(y, output, cache, params, activations_derivative)` returning gradients in the
   same order as `params` (a list of `(dW, db)`).
3. `numerical_gradient(loss_function, params, index, eps=1e-5)` returning the numerical gradient
   of a single weight (`index` = `(layer, row, col)` inside W).
4. `gradient_check(loss_function, params, analytic, eps=1e-5)` returning the largest relative difference.""",
            starter_code="""import numpy as np


def mlp_forward(X, params, activations):
    pass


def mlp_backward(y, output, cache, params, activations_derivative):
    pass


def numerical_gradient(loss_function, params, index, eps=1e-5):
    pass


def gradient_check(loss_function, params, analytic, eps=1e-5):
    pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import mlp_forward

def test_forward_shape():
    rng = np.random.default_rng(0)
    params = [(rng.normal(size=(3, 4)), np.zeros(4)), (rng.normal(size=(4, 2)), np.zeros(2))]
    output, cache = mlp_forward(rng.normal(size=(5, 3)), params, [lambda z: np.maximum(0, z)])
    assert output.shape == (5, 2)
    assert len(cache) == 2
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import mlp_forward, mlp_backward, numerical_gradient, gradient_check

RELU = lambda z: np.maximum(0, z)          # noqa: E731
RELU_D = lambda z: (z > 0).astype(float)   # noqa: E731


def build(seed=0):
    rng = np.random.default_rng(seed)
    return [
        (rng.normal(scale=0.3, size=(3, 5)), np.zeros(5)),
        (rng.normal(scale=0.3, size=(5, 1)), np.zeros(1)),
    ]


def mse(output, y):
    return float(((output - y) ** 2).mean())


def test_cache_contents():
    params = build()
    X = np.random.default_rng(1).normal(size=(4, 3))
    _, cache = mlp_forward(X, params, [RELU])
    assert len(cache) == 2
    assert cache[0][0].shape == (4, 3)
    assert cache[0][2].shape == (4, 5)

def test_backward_shapes():
    params = build()
    X = np.random.default_rng(2).normal(size=(4, 3))
    y = np.random.default_rng(3).normal(size=(4, 1))
    output, cache = mlp_forward(X, params, [RELU])
    grads = mlp_backward(y, output, cache, params, [RELU_D])
    assert len(grads) == 2
    assert grads[0][0].shape == params[0][0].shape
    assert grads[1][1].shape == params[1][1].shape

def test_gradient_matches_numerical():
    params = build(seed=4)
    X = np.random.default_rng(5).normal(size=(6, 3))
    y = np.random.default_rng(6).normal(size=(6, 1))
    output, cache = mlp_forward(X, params, [RELU])
    grads = mlp_backward(y, output, cache, params, [RELU_D])

    def loss():
        return mse(mlp_forward(X, params, [RELU])[0], y)

    for layer in range(2):
        for row in range(grads[layer][0].shape[0]):
            for col in range(grads[layer][0].shape[1]):
                numeric = numerical_gradient(loss, params, (layer, row, col))
                assert abs(numeric - grads[layer][0][row, col]) < 1e-6

def test_gradient_check_small():
    params = build(seed=7)
    X = np.random.default_rng(8).normal(size=(5, 3))
    y = np.random.default_rng(9).normal(size=(5, 1))
    output, cache = mlp_forward(X, params, [RELU])
    grads = mlp_backward(y, output, cache, params, [RELU_D])

    def loss():
        return mse(mlp_forward(X, params, [RELU])[0], y)

    difference = gradient_check(loss, params, grads)
    assert difference < 1e-5

def test_deep_network_forward():
    rng = np.random.default_rng(10)
    params = [
        (rng.normal(scale=0.2, size=(4, 6)), np.zeros(6)),
        (rng.normal(scale=0.2, size=(6, 6)), np.zeros(6)),
        (rng.normal(scale=0.2, size=(6, 3)), np.zeros(3)),
    ]
    output, cache = mlp_forward(rng.normal(size=(7, 4)), params, [RELU, RELU])
    assert output.shape == (7, 3)
    assert len(cache) == 3
"""},
            reference_solution="""import numpy as np


def mlp_forward(X, params, activations):
    cache = []
    output = np.asarray(X, dtype=float)
    for index, (W, b) in enumerate(params):
        inputs = output
        z = inputs @ W + b
        if index < len(params) - 1:
            output = activations[index](z)
        else:
            output = z
        cache.append((inputs, z, output))
    return output, cache


def mlp_backward(y, output, cache, params, activations_derivative):
    target = np.asarray(y, dtype=float).reshape(output.shape)
    n = len(target)
    grads = [None] * len(params)
    dz = 2 * (output - target) / n
    for index in range(len(params) - 1, -1, -1):
        inputs, z, activation_output = cache[index]
        dW = inputs.T @ dz
        db = dz.sum(axis=0)
        grads[index] = (dW, db)
        if index > 0:
            dinputs = dz @ params[index][0].T
            dz = dinputs * activations_derivative[index - 1](cache[index - 1][1])
    return grads


def numerical_gradient(loss_function, params, index, eps=1e-5):
    layer, row, col = index
    W = params[layer][0]
    original = W[row, col]
    W[row, col] = original + eps
    plus = loss_function()
    W[row, col] = original - eps
    minus = loss_function()
    W[row, col] = original
    return (plus - minus) / (2 * eps)


def gradient_check(loss_function, params, analytic, eps=1e-5):
    worst = 0.0
    for layer, (dW, _db) in enumerate(analytic):
        for row in range(dW.shape[0]):
            for col in range(dW.shape[1]):
                numeric = numerical_gradient(loss_function, params, (layer, row, col), eps)
                scale = max(abs(numeric) + abs(dW[row, col]), 1e-12)
                worst = max(worst, abs(numeric - dW[row, col]) / scale)
    return float(worst)
""",
            hints=(
                "Cache `(inputs, z, a)` for every layer: backprop needs all three.",
                "The MSE derivative at the output is `2 * (output - target) / n`.",
                "Scale the relative difference by the sum of the magnitudes, not by the analytic value alone.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب صنف `MLP` كامل التدريب:
- `__init__(layer_sizes, learning_rate=0.05, seed=0)` (مثل `[2, 16, 16, 1]`).
- `fit(X, y, epochs=2000)` بالانتشار العكسي على الانتروبيا المتقاطعة الثنائية
  (الطبقات المخفية `tanh`، والمخرج `sigmoid`).
- `predict_proba(X)`, `predict(X, threshold=0.5)` و`loss_history_`.

يجب أن يحقق دقة اختبار ≥ 0.9 على `make_moons(n_samples=400, noise=0.2, random_state=0)`
بتقسيم `test_size=0.25, random_state=0`.""",
            brief_en="""Write a fully trainable `MLP` class:
- `__init__(layer_sizes, learning_rate=0.05, seed=0)` (for example `[2, 16, 16, 1]`).
- `fit(X, y, epochs=2000)` by backpropagation on binary cross-entropy
  (hidden layers use `tanh`, the output uses `sigmoid`).
- `predict_proba(X)`, `predict(X, threshold=0.5)` and `loss_history_`.

It must reach test accuracy >= 0.9 on `make_moons(n_samples=400, noise=0.2, random_state=0)`
split with `test_size=0.25, random_state=0`.""",
            independent=True,
            starter_code="""import numpy as np


class MLP:
    def __init__(self, layer_sizes, learning_rate=0.05, seed=0):
        pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import MLP

def test_forward_shape():
    X = np.random.default_rng(0).normal(size=(10, 2))
    net = MLP([2, 8, 1], seed=0)
    assert net.predict_proba(X).shape == (10, 1)
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from main import MLP

X, y = make_moons(n_samples=400, noise=0.2, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

def test_learns_moons():
    net = MLP([2, 16, 16, 1], learning_rate=0.1, seed=0).fit(X_train, y_train, epochs=3000)
    accuracy = float((net.predict(X_test).ravel() == y_test).mean())
    assert accuracy >= 0.9, accuracy

def test_probabilities_valid():
    net = MLP([2, 8, 1], seed=1).fit(X_train, y_train, epochs=200)
    probabilities = net.predict_proba(X_test)
    assert probabilities.min() > 0.0 and probabilities.max() < 1.0

def test_loss_decreases():
    net = MLP([2, 16, 1], learning_rate=0.1, seed=2).fit(X_train, y_train, epochs=500)
    assert len(net.loss_history_) == 500
    assert net.loss_history_[-1] < net.loss_history_[0]

def test_overfits_tiny_batch():
    net = MLP([2, 32, 32, 1], learning_rate=0.2, seed=3).fit(X_train[:8], y_train[:8], epochs=2000)
    assert float((net.predict(X_train[:8]).ravel() == y_train[:8]).mean()) == 1.0

def test_predict_shape_and_values():
    net = MLP([2, 8, 1], seed=4).fit(X_train, y_train, epochs=100)
    predictions = net.predict(X_test)
    assert predictions.shape == (len(y_test), 1)
    assert set(np.unique(predictions)).issubset({0, 1})
"""},
            reference_solution="""import numpy as np


class MLP:
    def __init__(self, layer_sizes, learning_rate=0.05, seed=0):
        self.sizes = list(layer_sizes)
        self.learning_rate = float(learning_rate)
        self.seed = int(seed)
        self.loss_history_ = []
        rng = np.random.default_rng(self.seed)
        self.weights = []
        self.biases = []
        for inputs, outputs in zip(self.sizes[:-1], self.sizes[1:]):
            self.weights.append(rng.normal(scale=np.sqrt(2.0 / inputs), size=(inputs, outputs)))
            self.biases.append(np.zeros(outputs))

    def _forward(self, X):
        activations = [np.asarray(X, dtype=float)]
        pre_activations = []
        for index, (W, b) in enumerate(zip(self.weights, self.biases)):
            z = activations[-1] @ W + b
            pre_activations.append(z)
            activations.append(np.tanh(z) if index < len(self.weights) - 1 else self._sigmoid(z))
        return activations, pre_activations

    @staticmethod
    def _sigmoid(z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

    def predict_proba(self, X):
        return self._forward(X)[0][-1]

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

    def fit(self, X, y, epochs=2000):
        data = np.asarray(X, dtype=float)
        target = np.asarray(y, dtype=float).reshape(-1, 1)
        n = len(data)
        for _ in range(int(epochs)):
            activations, pre_activations = self._forward(data)
            probabilities = activations[-1]
            clipped = np.clip(probabilities, 1e-12, 1 - 1e-12)
            self.loss_history_.append(
                float(-(target * np.log(clipped) + (1 - target) * np.log(1 - clipped)).mean())
            )
            dz = (probabilities - target) / n
            for index in range(len(self.weights) - 1, -1, -1):
                dW = activations[index].T @ dz
                db = dz.sum(axis=0)
                dinputs = dz @ self.weights[index].T
                dz = dinputs * (1 - np.tanh(pre_activations[index - 1]) ** 2) if index > 0 else None
                self.weights[index] -= self.learning_rate * dW
                self.biases[index] -= self.learning_rate * db
        return self
""",
        ),
        transfer_ar="استخدم `MLP` في Neural Civilization لتعلّم سياسة مشاركة الموارد.",
        transfer_en="Use `MLP` in Neural Civilization to learn a resource-sharing policy.",
        references=(
            ("Backpropagation on Wikipedia", "https://en.wikipedia.org/wiki/Backpropagation"),
            ("Stanford UFLDL - gradient checking", "http://ufldl.stanford.edu/tutorial/supervised/DebuggingGradientChecking/"),
        ),
    ),
    CurriculumModule(
        id="l8.optimizers_regularization",
        level=8,
        order_index=3,
        domain="deep_learning",
        title_ar="المُحسِّنات والتنظيم",
        title_en="Optimizers and regularisation",
        summary_ar="SGD مع زخم، Adam، تنظيم L2، وإيقاف مبكر.",
        summary_en="SGD with momentum, Adam, L2 regularisation and early stopping.",
        explanation_ar="""نزول التدرج العادي يعاني من بطء في الأودية الضيقة ومن تذبذب في الأودية الحادة.
المُحسِّنات تحل ذلك بتكييف حجم الخطوة:

- **Momentum**: يتراكم اتجاهاً سابقاً `v = βv + g` ثم `w -= lr·v`. يسرّع الاتجاهات الثابتة.
- **RMSProp**: يقسّم على جذر متوسط مربع التدرج، فيخفّف التذبذب.
- **Adam**: يجمع الاثنين مع تصحيح الانحياز:
  `m = β₁m + (1-β₁)g`، `v = β₂v + (1-β₂)g²`،
  `m̂ = m/(1-β₁ᵗ)`، `v̂ = v/(1-β₂ᵗ)`،
  `w -= lr · m̂/(√v̂ + ε)`.
  هو الافتراضي الآمن (`lr ≈ 1e-3`).

لمنع التعلّم الزائد:
- **تنظيم L2 (weight decay)**: أضف `λ‖w‖²` للخسارة، أو اطرح `lr·λ·w` من التحديث،
- **Dropout**: عطّل نسبة من العصبونات عشوائياً أثناء التدريب (ليس هنا: نتعامل مع numpy فقط)،
- **الإيقاف المبكر**: راقب خسارة التحقق وأوقف عندما تتوقف عن التحسّن — أبسط وأرخص وسيلة.

احتفظ بأفضل أوزان رأيتها على التحقق، لا بآخر أوزان.""",
        explanation_en="""Plain gradient descent crawls along narrow valleys and oscillates in steep ones.
Optimizers fix that by adapting the step size:

- **Momentum**: accumulates a direction `v = beta*v + g`, then `w -= lr*v`. Speeds up consistent directions.
- **RMSProp**: divides by the root mean square of the gradient, damping the oscillation.
- **Adam**: combines both with bias correction:
  `m = b1*m + (1-b1)g`, `v = b2*v + (1-b2)g^2`,
  `m_hat = m/(1-b1^t)`, `v_hat = v/(1-b2^t)`,
  `w -= lr * m_hat/(sqrt(v_hat) + eps)`.
  It is the safe default (`lr ~ 1e-3`).

To fight overfitting:
- **L2 regularisation (weight decay)**: add `lambda*||w||^2` to the loss, or subtract `lr*lambda*w` in the update,
- **Dropout**: disable a random fraction of units during training (out of scope here: numpy only),
- **Early stopping**: watch the validation loss and stop when it stops improving - the simplest
  and cheapest defence.

Keep the best weights you saw on validation, not the last ones.""",
        skills=("dl.training",),
        prerequisites=("l8.backprop_mlp",),
        example_code="""import numpy as np


class SGD:
    def __init__(self, learning_rate=0.05):
        self.lr = learning_rate

    def step(self, params, grads):
        return [param - self.lr * grad for param, grad in zip(params, grads)]


class Momentum:
    def __init__(self, learning_rate=0.05, beta=0.9):
        self.lr, self.beta = learning_rate, beta
        self.velocity = None

    def step(self, params, grads):
        if self.velocity is None:
            self.velocity = [np.zeros_like(grad) for grad in grads]
        self.velocity = [self.beta * v + grad for v, grad in zip(self.velocity, grads)]
        return [param - self.lr * v for param, v in zip(params, self.velocity)]


class Adam:
    def __init__(self, learning_rate=0.01, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = learning_rate, beta1, beta2, eps
        self.m = self.v = None
        self.t = 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(grad) for grad in grads]
            self.v = [np.zeros_like(grad) for grad in grads]
        self.t += 1
        self.m = [self.b1 * m + (1 - self.b1) * g for m, g in zip(self.m, grads)]
        self.v = [self.b2 * v + (1 - self.b2) * (g ** 2) for v, g in zip(self.v, grads)]
        corrected_m = [m / (1 - self.b1 ** self.t) for m in self.m]
        corrected_v = [v / (1 - self.b2 ** self.t) for v in self.v]
        return [p - self.lr * m / (np.sqrt(v) + self.eps)
                for p, m, v in zip(params, corrected_m, corrected_v)]


def objective(weights):
    \"\"\"A steep, narrow valley: flat along w0, sharp along w1.\"\"\"
    return 0.01 * weights[0] ** 2 + 5 * weights[1] ** 2


def gradient(weights):
    return np.array([0.02 * weights[0], 10 * weights[1]])


weights = np.array([10.0, 1.0])
for name, optimizer in [("sgd", SGD(0.05)), ("momentum", Momentum(0.05)), ("adam", Adam(0.5))]:
    current = weights.copy()
    optimizer.__init__(*(optimizer.lr,)) if name != "adam" else None
    opt = type(optimizer)(*([optimizer.lr] if name != "adam" else [0.5]))
    for _ in range(200):
        current = opt.step(current, gradient(current))
    print(f"{name:>9}: final loss {objective(current):.6f}")
""",
        example_notes_ar="جرّب تعريف `opt` داخل الحلقة: إعادة استخدام مُحسِّن مدرب يغيّر النتائج.",
        example_notes_en="Try redefining `opt` inside the loop: reusing a trained optimizer changes the results.",
        experiment_code="""import numpy as np
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

X, y = make_moons(n_samples=300, noise=0.25, random_state=3)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=3)
y_train, y_val = y_train.reshape(-1, 1).astype(float), y_val.reshape(-1, 1).astype(float)

rng = np.random.default_rng(0)
W1 = rng.normal(scale=np.sqrt(2 / 2), size=(2, 24))
b1 = np.zeros(24)
W2 = rng.normal(scale=np.sqrt(2 / 24), size=(24, 1))
b2 = np.zeros(1)


def forward(X):
    a1 = np.tanh(X @ W1 + b1)
    return a1, 1 / (1 + np.exp(-(a1 @ W2 + b2)))


def loss(p, target):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(-(target * np.log(p) + (1 - target) * np.log(1 - p)).mean())


def l2_term(l2):
    return l2 * (float((W1 ** 2).sum()) + float((W2 ** 2).sum()))


for l2 in (0.0, 0.001, 0.01):
    rng = np.random.default_rng(0)
    W1[:] = rng.normal(scale=np.sqrt(2 / 2), size=(2, 24))
    W2[:] = rng.normal(scale=np.sqrt(2 / 24), size=(24, 1))
    b1[:] = 0.0
    b2[:] = 0.0
    for _ in range(1500):
        a1, p = forward(X_train)
        dz = (p - y_train) / len(X_train)
        dW2 = a1.T @ dz + 2 * l2 * W2
        db2 = dz.sum(axis=0)
        dz1 = (dz @ W2.T) * (1 - a1 ** 2)
        dW1 = X_train.T @ dz1 + 2 * l2 * W1
        db1 = dz1.sum(axis=0)
        W1 -= 0.3 * dW1
        b1 -= 0.3 * db1
        W2 -= 0.3 * dW2
        b2 -= 0.3 * db2
    train_acc = float(((forward(X_train)[1] >= 0.5).astype(float) == y_train).mean())
    val_acc = float(((forward(X_val)[1] >= 0.5).astype(float) == y_val).mean())
    print(f"l2={l2:<6} train {train_acc:.3f}  val {val_acc:.3f}  |w| {np.sqrt(l2_term(1)):.2f}")
""",
        experiment_brief_ar="زد `l2` إلى 0.5 وشاهد انهيار الدقة: التنظيم الزائد يمنع التعلّم.",
        experiment_brief_en="Push `l2` to 0.5 and watch accuracy collapse: too much regularisation prevents learning.",
        task=TaskSpec(
            brief_ar="""اكتب أصناف المُحسِّنات بواجهة موحّدة `step(params, grads)` تُعيد المعاملات المحدَّثة:
1. `SGD(learning_rate=0.05)`.
2. `Momentum(learning_rate=0.05, beta=0.9)`.
3. `RMSProp(learning_rate=0.01, beta=0.99, eps=1e-8)`.
4. `Adam(learning_rate=0.01, beta1=0.9, beta2=0.999, eps=1e-8)`.

كلها تعمل على قوائم مصفوفات numpy، وتدعم نداءات `step` متتالية (تحافظ على الحالة).""",
            brief_en="""Write optimizer classes with a uniform `step(params, grads)` interface returning updated
parameters:
1. `SGD(learning_rate=0.05)`.
2. `Momentum(learning_rate=0.05, beta=0.9)`.
3. `RMSProp(learning_rate=0.01, beta=0.99, eps=1e-8)`.
4. `Adam(learning_rate=0.01, beta1=0.9, beta2=0.999, eps=1e-8)`.

All of them work on lists of numpy arrays and support repeated `step` calls (they keep state).""",
            starter_code="""import numpy as np


class SGD:
    def __init__(self, learning_rate=0.05):
        pass

    def step(self, params, grads):
        pass


class Momentum:
    def __init__(self, learning_rate=0.05, beta=0.9):
        pass

    def step(self, params, grads):
        pass


class RMSProp:
    def __init__(self, learning_rate=0.01, beta=0.99, eps=1e-8):
        pass

    def step(self, params, grads):
        pass


class Adam:
    def __init__(self, learning_rate=0.01, beta1=0.9, beta2=0.999, eps=1e-8):
        pass

    def step(self, params, grads):
        pass
""",
            public_tests={"test_public.py": """import numpy as np
from main import SGD

def test_sgd_step():
    params = [np.array([1.0])]
    grads = [np.array([2.0])]
    updated = SGD(learning_rate=0.1).step(params, grads)
    assert np.allclose(updated[0], [0.8])
"""},
            hidden_tests={"test_hidden.py": """import numpy as np
from main import SGD, Momentum, RMSProp, Adam

def minimise(optimizer, steps=300):
    params = [np.array([5.0, -5.0])]
    for _ in range(steps):
        grads = [2 * params[0]]
        params = optimizer.step(params, grads)
    return float((params[0] ** 2).sum())

def test_sgd_converges():
    assert minimise(SGD(learning_rate=0.05)) < 1e-6

def test_momentum_converges():
    assert minimise(Momentum(learning_rate=0.02, beta=0.9)) < 1e-6

def test_rmsprop_converges():
    assert minimise(RMSProp(learning_rate=0.1)) < 1e-6

def test_adam_converges():
    assert minimise(Adam(learning_rate=0.1)) < 1e-6

def test_zero_gradient_changes_nothing():
    params = [np.ones(3)]
    for optimizer in (SGD(), Momentum(), RMSProp(), Adam()):
        updated = optimizer.step([p.copy() for p in params], [np.zeros(3)])
        assert np.allclose(updated[0], params[0])

def test_state_persists():
    optimizer = Momentum(learning_rate=0.1, beta=0.9)
    params = [np.array([1.0])]
    params = optimizer.step(params, [np.array([1.0])])
    assert optimizer.velocity is not None

def test_multiple_parameter_groups():
    params = [np.ones((2, 3)), np.zeros(4)]
    grads = [np.full((2, 3), 0.1), np.full(4, -0.1)]
    for optimizer in (SGD(0.1), Momentum(0.1), RMSProp(0.1), Adam(0.1)):
        updated = optimizer.step([p.copy() for p in params], grads)
        assert updated[0].shape == (2, 3) and updated[1].shape == (4,)

def test_shapes_preserved():
    params = [np.ones((2, 2)), np.ones(3)]
    grads = [np.ones((2, 2)), np.ones(3)]
    updated = Adam(0.01).step([p.copy() for p in params], grads)
    assert all(a.shape == b.shape for a, b in zip(updated, params))
"""},
            reference_solution="""import numpy as np


class SGD:
    def __init__(self, learning_rate=0.05):
        self.lr = float(learning_rate)
        self.velocity = None

    def step(self, params, grads):
        return [param - self.lr * grad for param, grad in zip(params, grads)]


class Momentum:
    def __init__(self, learning_rate=0.05, beta=0.9):
        self.lr = float(learning_rate)
        self.beta = float(beta)
        self.velocity = None

    def step(self, params, grads):
        if self.velocity is None:
            self.velocity = [np.zeros_like(grad) for grad in grads]
        self.velocity = [self.beta * v + grad for v, grad in zip(self.velocity, grads)]
        return [param - self.lr * v for param, v in zip(params, self.velocity)]


class RMSProp:
    def __init__(self, learning_rate=0.01, beta=0.99, eps=1e-8):
        self.lr = float(learning_rate)
        self.beta = float(beta)
        self.eps = float(eps)
        self.accumulator = None

    def step(self, params, grads):
        if self.accumulator is None:
            self.accumulator = [np.zeros_like(grad) for grad in grads]
        self.accumulator = [self.beta * acc + (1 - self.beta) * (grad ** 2)
                            for acc, grad in zip(self.accumulator, grads)]
        return [param - self.lr * grad / (np.sqrt(acc) + self.eps)
                for param, grad, acc in zip(params, grads, self.accumulator)]


class Adam:
    def __init__(self, learning_rate=0.01, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr = float(learning_rate)
        self.b1 = float(beta1)
        self.b2 = float(beta2)
        self.eps = float(eps)
        self.m = None
        self.v = None
        self.t = 0

    def step(self, params, grads):
        if self.m is None:
            self.m = [np.zeros_like(grad) for grad in grads]
            self.v = [np.zeros_like(grad) for grad in grads]
        self.t += 1
        self.m = [self.b1 * m + (1 - self.b1) * g for m, g in zip(self.m, grads)]
        self.v = [self.b2 * v + (1 - self.b2) * (g ** 2) for v, g in zip(self.v, grads)]
        corrected_m = [m / (1 - self.b1 ** self.t) for m in self.m]
        corrected_v = [v / (1 - self.b2 ** self.t) for v in self.v]
        return [param - self.lr * m / (np.sqrt(v) + self.eps)
                for param, m, v in zip(params, corrected_m, corrected_v)]
""",
            hints=(
                "Every optimizer keeps one state list per parameter group, created on the first step.",
                "Adam needs bias correction: divide by `1 - beta**t` where `t` counts the steps.",
                "Add `eps` inside the square root, never outside, to avoid dividing by zero.",
            ),
        ),
        assessment=TaskSpec(
            brief_ar="""اكتب `train_with_early_stopping(make_model, X, y, X_val, y_val, epochs=2000, patience=50)`
تُعيد:

```python
{
  "epochs_run": int, "best_epoch": int, "best_val_loss": float,
  "train_history": [...], "val_history": [...], "stopped_early": bool
}
```

القواعد:
- درّب حقبة واحدة في كل مرة (النموذج يعرّف `fit(X, y, epochs=1)` مع تحديث تدريجي،
  و`loss(X, y)` و`predict_proba(X)`),
- سجّل خسارة التدريب وخسارة التحقق بعد كل حقبة،
- أوقف التدريب إذا لم يتحسّن خسارة التحقق لمدة `patience` حقبة متتالية،
- سجّل أفضل حقبة وقيمتها.""",
            brief_en="""Write `train_with_early_stopping(make_model, X, y, X_val, y_val, epochs=2000, patience=50)`
returning:

```python
{
  "epochs_run": int, "best_epoch": int, "best_val_loss": float,
  "train_history": [...], "val_history": [...], "stopped_early": bool
}
```

Rules:
- train one epoch at a time (the model exposes `fit(X, y, epochs=1)` with incremental updates,
  plus `loss(X, y)` and `predict_proba(X)`),
- record training and validation loss after every epoch,
- stop when the validation loss has not improved for `patience` consecutive epochs,
- record the best epoch and its value.""",
            independent=True,
            starter_code="""def train_with_early_stopping(make_model, X, y, X_val, y_val, epochs=2000, patience=50):
    pass
""",
            public_tests={"test_public.py": """from main import train_with_early_stopping

class Shrinking:
    \"\"\"A toy model whose validation loss improves and then worsens.\"\"\"

    def __init__(self):
        self.step = 0

    def fit(self, X, y, epochs=1):
        for _ in range(epochs):
            self.step += 1
        return self

    def loss(self, X, y):
        distance = abs(self.step - 10)
        return distance / 100 if len(X) > 3 else distance / 200

def test_runs_and_stops():
    X, y = [[0.0]] * 5, [0] * 5
    X_val, y_val = [[1.0]] * 3, [1] * 3
    report = train_with_early_stopping(Shrinking, X, y, X_val, y_val, epochs=200, patience=5)
    assert report["stopped_early"] is True
    assert report["best_epoch"] == 10
"""},
            hidden_tests={"test_hidden.py": """from main import train_with_early_stopping

class Shrinking:
    def __init__(self):
        self.step = 0

    def fit(self, X, y, epochs=1):
        for _ in range(epochs):
            self.step += 1
        return self

    def loss(self, X, y):
        distance = abs(self.step - 10)
        return distance / 100 if len(X) > 3 else distance / 200

X, y = [[0.0]] * 5, [0] * 5
X_val, y_val = [[1.0]] * 3, [1] * 3

def test_histories_have_same_length():
    report = train_with_early_stopping(Shrinking, X, y, X_val, y_val, epochs=100, patience=3)
    assert len(report["train_history"]) == len(report["val_history"])
    assert len(report["train_history"]) == report["epochs_run"]

def test_best_val_loss():
    report = train_with_early_stopping(Shrinking, X, y, X_val, y_val, epochs=100, patience=3)
    assert abs(report["best_val_loss"] - 0.0) < 1e-9

def test_stops_before_the_budget():
    report = train_with_early_stopping(Shrinking, X, y, X_val, y_val, epochs=500, patience=3)
    assert report["epochs_run"] < 500

def test_no_early_stop_when_improving():
    class AlwaysImproving:
        def __init__(self):
            self.step = 0

        def fit(self, X, y, epochs=1):
            self.step += epochs
            return self

        def loss(self, X, y):
            return 1.0 / (self.step + 1)

    report = train_with_early_stopping(AlwaysImproving, X, y, X_val, y_val, epochs=20, patience=5)
    assert report["stopped_early"] is False
    assert report["epochs_run"] == 20

def test_patience_one():
    report = train_with_early_stopping(Shrinking, X, y, X_val, y_val, epochs=100, patience=1)
    assert report["best_epoch"] == 10
    assert report["epochs_run"] == 11
"""},
            reference_solution="""def train_with_early_stopping(make_model, X, y, X_val, y_val, epochs=2000, patience=50):
    model = make_model()
    train_history = []
    val_history = []
    best_epoch = 0
    best_val_loss = float("inf")
    epochs_run = 0
    waiting = 0

    for epoch in range(1, int(epochs) + 1):
        model.fit(X, y, epochs=1)
        train_loss = float(model.loss(X, y))
        val_loss = float(model.loss(X_val, y_val))
        train_history.append(train_loss)
        val_history.append(val_loss)
        epochs_run = epoch

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            waiting = 0
        else:
            waiting += 1
            if waiting >= int(patience):
                break

    return {
        "epochs_run": epochs_run,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "train_history": train_history,
        "val_history": val_history,
        "stopped_early": epochs_run < int(epochs),
    }
""",
        ),
        transfer_ar="استخدم الإيقاف المبكر في Model Olympics لمنع تعلّم نموذجك الزائد.",
        transfer_en="Use early stopping in Model Olympics to stop your model from overfitting.",
        references=(
            ("Adam paper (Kingma & Ba, 2014)", "https://arxiv.org/abs/1412.6980"),
            ("An overview of gradient descent optimization algorithms", "https://ruder.io/optimizing-gradient-descent/"),
        ),
    ),
]
