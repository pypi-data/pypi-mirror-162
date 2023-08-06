# Analysis tools for Machine learning projects

## 1. Usage
```bash
# Load repository manually
$ git clone https://github.com/djy-git/analysis-tools.git 

# Install with Pypi
$ pip install analysis-tools
```

## 2. Tutorial
[examples/titanic/eda.ipynb](https://github.com/djy-git/analysis-tools/blob/main/examples/titanic/eda.ipynb)를 참고

```python
from analysis_tools.eda import *

data   = pd.DataFrame(..)
target = 'survived'

num_features       = ['age', 'sibsp', 'parch', 'fare']
cat_features       = data.columns.drop(num_features)
data[num_features] = data[num_features].astype('float32')
data[cat_features] = data[cat_features].astype('string')

plot_missing_value(data)
plot_features(data)
plot_features_target(data, target)
plot_corr(data.corr())
```

![](https://github.com/djy-git/analysis-tools/blob/main/examples/titanic/visualization/Missing%20value_1.png?raw=true)
![](https://github.com/djy-git/analysis-tools/blob/main/examples/titanic/visualization/Features_1.png?raw=true)
![](https://github.com/djy-git/analysis-tools/blob/main/examples/titanic/visualization/Features%20vs%20Target_1.png?raw=true)
![](https://github.com/djy-git/analysis-tools/blob/main/examples/titanic/visualization/Correlation%20matrix_1.png?raw=true)
