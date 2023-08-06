### Calculates body mas index (BMI) based on a given set of parameters such as weight, height, gender, age and life-style

```bash
python setup.py sdist bdist_wheel
```

### upload
```bash
pip install twine

twine upload --repository-url https://test.pypi.org/legacy/ dist/*
twine upload dist/*

python -m twine upload --repository testpypi dist/*
python -m twine upload --repository pypi dist/*

pip install -i https://test.pypi.org/simple/ --no-deps bmi-calculator-0.1.0
```

### Usage:
```python

import bmi_kalculator as bmi
>> bm = bmi.PersonForBMI(25, 150, 134, 'female')
>> bm.calculate_bmi()
>> bm.conclusions()

# OR
from bmi_kalculator import PersonForBMI as bmi
>> bm = bmi(23, 45, 56, 'f')
>> bm.calculate_bmi()
>> bm.conclusions()

```